import asyncio
import gc
import json
import jwt
import os
import shutil
import time
from datetime import datetime, timezone

import aioboto3
import torch
import transformers.utils.logging as transformers_logging
from transformers import AutoModelForCausalLM, AutoTokenizer

from app import logger
from app.src.constants import BUCKET, LLM_MAP_S3_KEY, LLM_S3_KEY, NO_DEPLOYED_MODEL_MSG, PROP_PATH
from app.src.utils import extract_tar, get_directory_size, get_target_paths
from app.src.constants import LICENSE_PATH
from license_validator import LicenseValidator
transformers_logging.disable_default_handler()
transformers_logging.disable_progress_bar()

transformers_logging.set_verbosity(transformers_logging.CRITICAL)


class JslLlm:
    def __init__(self):
        self.llm = None
        self.llm_name = None
        self.tokenizer = None
        self.device = None
        self.model_max_len = None
        self.deployed_at = None
        self._llms_info = None
        self.spark_nlp_license_key = None
        with open(LICENSE_PATH) as _license:
            for k, v in json.loads(_license.read()).items():
                os.environ[k] = v
                if k == "SPARK_NLP_LICENSE":
                    self.spark_nlp_license_key = v
        logger.info(".")
        self.lv = LicenseValidator()
        logger.info("..")
        self.lv.trigger_license_check(fetch_credentials=True)
        time.sleep(20)
        logger.info("...")

    def is_inference_scope(self):
        if not (
            scopes := jwt.decode(
                self.spark_nlp_license_key, options={"verify_signature": False}
            ).get("scope")
        ):
            # Very old airgap licenses may not have scopes
            return True
        return any(True for each in scopes if "inference" in each)

    def beat_check(self):
        logger.debug("beat.")
        self.lv.is_license_valid(wait=True)
        logger.info("^")

    def set_aws_keys(self):
        self.lv.trigger_license_check(fetch_credentials=True)
        aws_creds = self.lv.get_aws_credentials()
        os.environ["AWS_ACCESS_KEY_ID"] = aws_creds["accessKeyId"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_creds["secretAccessKey"]
        os.environ["AWS_SESSION_TOKEN"] = aws_creds.get("sessionToken")
        logger.info("AWS Keys Set!")

    @property
    def status(self):
        if self.llm:
            return f"Model {self.llm_name} loaded with max context length: {self.model_max_len}"
        return NO_DEPLOYED_MODEL_MSG

    def is_llm_model_ready(self):
        return True if self.llm_name else False

    @property
    async def friendly_names(self):
        return sorted(list(self.llms_info.keys()))

    async def download_from_s3(self, llm_name: str):
        self.llm_name = llm_name
        extract_path, tar_file_path = get_target_paths(llm_name)
        if os.path.isdir(extract_path):
            logger.info(f"skipping fetch: {llm_name}")
            return extract_path
        self.set_aws_keys()

        logger.info(f"fetching started: {llm_name}")
        os.makedirs(extract_path, exist_ok=True)
        session = aioboto3.Session()
        # If llms_info is not set
        if not self.llms_info:
            await self.setup_llms_info()
        actual_name = self.llms_info[llm_name]["s3_key_name"]
        key = f"{LLM_S3_KEY}/{actual_name}"
        async with session.client("s3") as client:
            response = await client.get_object(Bucket=BUCKET, Key=key)
            with open(tar_file_path, "wb") as file:
                async for chunk in response["Body"].iter_chunks(chunk_size=1024 * 1024):
                    file.write(chunk)
        logger.info(f"fetch completed: {llm_name}")
        await extract_tar(tar_file_path, extract_path)
        os.remove(tar_file_path)
        return extract_path

    async def load_model(self, llm_name, extract_path_or_remote_name, device_id, hf_token=None):
        gc.collect()
        torch.cuda.empty_cache()

        self.device = device_id
        args = dict(
            device_map=self.device,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            use_auth_token=hf_token,
        )
        self.llm = await asyncio.to_thread(
            AutoModelForCausalLM.from_pretrained, extract_path_or_remote_name, **args
        )
        self.llm.eval()
        args = dict(use_fast=True, device_map=self.device, use_auth_token=hf_token)
        self.tokenizer = await asyncio.to_thread(
            AutoTokenizer.from_pretrained, extract_path_or_remote_name, **args
        )
        self.llm_name = llm_name
        self.model_max_len = self.llm.config.max_position_embeddings
        self.delete_artifacts()
        self.deployed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")

    async def get_progress(self, llm_name):
        extract_path, tar_file_path = get_target_paths(llm_name)
        size = get_directory_size(extract_path)
        llm_info = self.llms_info.get(llm_name, {})
        if not (total_size := llm_info.get("size_in_bytes")):
            return "n/a"
        # Assuming extraction takes double the size
        approx_size_after_extraction = total_size * 2
        current_size_in_percentage = int(size * 100 / approx_size_after_extraction)
        return f"{current_size_in_percentage} %"

    @staticmethod
    async def __s3_object_info(client, v):
        response = await client.head_object(Bucket=BUCKET, Key=f"{LLM_S3_KEY}/{v}")
        if (content_size := response["ContentLength"] / 1024 / 1024) > 512:
            content_size /= 1024
            pretty_size = f"{content_size:.2f} GB"
        else:
            pretty_size = f"{content_size:.2f} MB"
        return {"size": pretty_size, "size_in_bytes": response["ContentLength"]}

    @property
    def llms_info(self):
        return self._llms_info

    async def setup_llms_info(self):
        self.set_aws_keys()
        session = aioboto3.Session()
        llms_info = dict()
        async with session.client("s3") as client:
            response = await client.get_object(Bucket=BUCKET, Key=LLM_MAP_S3_KEY)
            async for chunk in response["Body"].iter_chunks(chunk_size=1024):
                llms_map = json.loads(chunk)
                for k, v in llms_map.items():
                    value = await self.__s3_object_info(client, v)
                    value["s3_key_name"] = v
                    llms_info[k] = value
        self._llms_info = llms_info

    def offload_model(self):
        if self.llm is None:
            return NO_DEPLOYED_MODEL_MSG

        del self.llm
        del self.tokenizer
        gc.collect()
        torch.cuda.empty_cache()
        _temp_llm_model = self.llm_name
        self.llm_name = None
        self.llm = None
        self.tokenizer = None
        self.model_max_len = None
        self.deployed_at = None
        return f"Model {_temp_llm_model} unloaded."

    async def get_prediction(self, prompt, max_new_tokens, temperature):
        if self.llm is None:
            return NO_DEPLOYED_MODEL_MSG
        template_string = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], tokenize=False
        )
        input_ids = self.tokenizer(template_string, truncation=True, return_tensors="pt")
        input_tokens = len(input_ids[0])
        if self.device == "auto":
            input_ids = input_ids.to(self.llm.device.type)
        else:
            input_ids = input_ids.to(self.device)
        args = dict(temperature=temperature, max_new_tokens=max_new_tokens)
        resps = await asyncio.to_thread(self.llm.generate, **input_ids, **args)
        output = self.tokenizer.decode(resps[0][input_tokens:], skip_special_tokens=True)
        # output token length
        output_tokens_len = len(self.tokenizer.encode(output, truncation=True))
        return output, output_tokens_len

    async def get_input_token_len(self, prompt):
        return len(self.tokenizer.tokenize(prompt))

    @staticmethod
    def delete_artifacts():
        shutil.rmtree(PROP_PATH, ignore_errors=True)
        shutil.rmtree("/app/.nv", ignore_errors=True)
        shutil.rmtree("/app/.cache", ignore_errors=True)
