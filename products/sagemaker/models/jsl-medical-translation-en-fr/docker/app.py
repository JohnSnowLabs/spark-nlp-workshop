import json
import logging
import os
import sys
import torch
import gc
from collections import defaultdict
from typing import List, Union, Any, Dict, Tuple
from fastapi import FastAPI, Request, HTTPException
from peft import PeftModel
from transformers import M2M100Tokenizer, AutoModelForSeq2SeqLM
from pydantic import BaseModel, validator, ValidationError
from http import HTTPStatus
from fastapi.responses import Response


# Logger configuration
def get_logger(logger_name):
    log_level = os.environ.get("LOG_LEVEL", "ERROR").upper()
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(
        logging.Formatter("%(name)s [%(asctime)s] [%(levelname)s] %(message)s")
    )
    logger.addHandler(handler)
    return logger


logger = get_logger("prediction-service")


class FormatInput(BaseModel):
    text: Union[str, List[str]]
    direction: str = "en_to_fr"

    @validator("text")
    def validate_text_format(cls, v: Any) -> Union[str, List[str]]:
        if isinstance(v, str):
            return [v]
        elif isinstance(v, list):
            if not all(isinstance(item, str) for item in v):
                raise ValueError(
                    "Invalid input format. All elements in 'text' list must be strings."
                )
            return v
        else:
            raise ValueError(
                "Invalid input format. 'text' field must be a string or a list of strings."
            )

    @validator("direction")
    def validate_direction(cls, v: str) -> str:
        if v not in ["en_to_fr", "fr_to_en"]:
            raise ValueError(
                "Invalid translation direction. Supported directions: 'en_to_fr', 'fr_to_en'."
            )
        return v


class ModelLoader:
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _batch_size = (
        1
        if _device == torch.device("cpu")
        else (
            2 if torch.cuda.get_device_properties(0).total_memory < 16 * 1024**3 else 4
        )
    )
    base_dir = "/opt/ml/model"
    base_model_dir = "base_model"

    @classmethod
    def find_directory(cls, base_dir, target_dir):
        for root, dirs, files in os.walk(base_dir):
            if target_dir in dirs:
                return os.path.join(root, target_dir)
        raise FileNotFoundError(
            f"Directory '{target_dir}' not found under '{base_dir}' or its subdirectories."
        )

    @classmethod
    def load_base_model(cls):
        base_model_path = cls.find_directory(cls.base_dir, cls.base_model_dir)
        base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_path).to(
            cls._device
        )
        return base_model

    @classmethod
    def load_model(cls, src_lang, targ_lang) -> Tuple:
        base_model = ModelLoader.load_base_model()
        model_path = cls.find_directory(
            cls.base_dir, f"checkpoint_{src_lang}_{targ_lang}"
        )
        tokenizer = M2M100Tokenizer.from_pretrained(f"{model_path}/checkpoint-41775")
        tokenizer.src_lang, tokenizer.tgt_lang = src_lang, targ_lang
        model = PeftModel.from_pretrained(
            base_model,
            f"{model_path}/checkpoint-41775",
        ).to(cls._device)

        model.eval()
        gc.collect()
        torch.cuda.empty_cache()

        return model, tokenizer


try:
    MODELS, TOKENIZERS = {}, {}

    for src_lang, targ_lang in [("en", "fr"), ("fr", "en")]:
        model, tokenizer = ModelLoader.load_model(
            src_lang=src_lang, targ_lang=targ_lang
        )
        key = f"{src_lang}_to_{targ_lang}"
        MODELS[key] = model
        TOKENIZERS[key] = tokenizer

    DEVICE, BATCH_SIZE = ModelLoader._device, ModelLoader._batch_size

except Exception as e:
    logger.error(f"An unexpected error occurred while loading the model: {e}")
    raise


app = FastAPI()


@app.get("/ping")
async def readiness_probe():
    return "Ready"


def infer_batch(in_text: List[str], direction: str) -> List[str]:

    model = MODELS[direction]
    tokenizer = TOKENIZERS[direction]

    out_text = []
    for i in range(0, len(in_text), BATCH_SIZE):
        batch = in_text[i : i + BATCH_SIZE]
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=1024,
        ).to(DEVICE)

        with torch.no_grad():
            outputs = model.generate(**inputs)

        out_text.extend(tokenizer.batch_decode(outputs, skip_special_tokens=True))

        if (i // BATCH_SIZE + 1) % 100 == 0:
            torch.cuda.empty_cache()

    return out_text


def get_predictions_from_json_data(input_data: str) -> Dict:
    input_json = json.loads(input_data)
    input_data_obj = FormatInput(**input_json)
    predictions = infer_batch(input_data_obj.text, input_data_obj.direction)

    return {
        "predictions": predictions,
        "consumed_units": len(predictions),
    }


def get_predictions_from_jsonlines_data(input_data: str) -> Dict:
    grouped_dict = defaultdict(lambda: {"text": [], "index": []})

    for line_number, line in enumerate(input_data.splitlines()):
        try:
            json_data = json.loads(line)
            sample = FormatInput(**json_data)
            grouped_dict[sample.direction]["text"].extend(sample.text)
            grouped_dict[sample.direction]["index"].append(line_number)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON line at line {line_number}: {line}") from e
        except KeyError as e:
            raise ValueError(
                f"Missing 'text' key in JSON line at line {line_number}: {line}"
            ) from e

    predictions = []
    for direction, data in grouped_dict.items():
        response = infer_batch(data["text"], direction)
        predictions.append({"response": response, "index": data["index"]})
    return {
        "predictions": predictions,
        "consumed_units": len(input_data.splitlines()),
    }


def get_json_response(
    predictions: List[str],
    **kwargs,
):
    return json.dumps({"predictions": predictions}, ensure_ascii=False)


def get_jsonlines_response(
    predictions: List[dict],
    **kwargs,
):
    index_to_response = {}

    for item in predictions:
        for idx, res in zip(item["index"], item["response"]):
            index_to_response[idx] = res

    sorted_responses = [index_to_response[idx] for idx in sorted(index_to_response)]

    return "\n".join(
        json.dumps({"predictions": res}, ensure_ascii=False) for res in sorted_responses
    )


SUPPORTED_REQUEST_MIMETYPES = ["application/json", "application/jsonlines"]
SUPPORTED_RESPONSE_MIMETYPES = ["application/json", "application/jsonlines"]


@app.post("/invocations")
async def invocations(request: Request):
    try:
        input_data = await request.body()
        content_type = request.headers.get("content-type", "application/json")
        accept = request.headers.get("accept", "application/json")

        if content_type not in SUPPORTED_REQUEST_MIMETYPES:
            raise HTTPException(
                status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                detail=f"Invalid Content-Type. Supported Content-Types: {', '.join(SUPPORTED_REQUEST_MIMETYPES)}",
            )

        if content_type == "application/json":
            model_response = get_predictions_from_json_data(input_data.decode("utf-8"))
        elif content_type == "application/jsonlines":
            model_response = get_predictions_from_jsonlines_data(
                input_data.decode("utf-8")
            )

        response_mimetype = (
            accept if accept in SUPPORTED_RESPONSE_MIMETYPES else content_type
        )

        if response_mimetype == "application/jsonlines":
            response = get_jsonlines_response(**model_response)
        elif response_mimetype == "application/json":
            response = get_json_response(**model_response)

        return Response(
            content=response,
            media_type=response_mimetype,
            headers={
                "X-Amzn-Inference-Metering": json.dumps(
                    {
                        "Dimension": "inference.count",
                        "ConsumedUnits": model_response.get("consumed_units", 0),
                    }
                )
            },
        )
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Internal server error"
        )
