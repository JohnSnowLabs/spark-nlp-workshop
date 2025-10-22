import os
import time
from datetime import datetime, timezone
from typing import Dict, Optional

import GPUtil
import torch
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app import logger
from app.src.constants import BUSY_STATUS, Status
from app.src.jsl_llm import JslLlm
from app.src.utils import clear_opt

jsl_llm = JslLlm()

logger.info("********************* APP IS READY *********************")


class DeployRequest(BaseModel):
    force: Optional[bool] = False
    llm_name: str
    device: Optional[str] = "auto"
    hf_token: Optional[str] = None


class GenerateRequest(BaseModel):
    text: str
    max_new_tokens: Optional[int] = 128
    temperature: Optional[float] = 0.1


async def before_request(request: Request):
    logger.debug(f"Received request: {request.method} {request.url}")
    if os.getenv("MINIMAL_SETUP"):
        return

    try:
        jsl_llm.beat_check()
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Issue in license: {ex}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not jsl_llm.is_inference_scope():
        raise HTTPException(status_code=400, detail="invalid license type")


route = APIRouter(dependencies=[Depends(before_request)])

jobs: Dict[str, str] = {}


async def deployment_task(llm_name: str, device_id: str, force: bool, hf_token: str):
    jobs.clear()
    jobs[llm_name] = Status.DEPLOYING.value
    jsl_llm.offload_model()
    if not jsl_llm.llms_info:
        await jsl_llm.setup_llms_info()
    if force:
        await clear_opt()
    extract_path, remote_name = None, None
    try:
        if llm_name not in jsl_llm.llms_info:
            remote_name = llm_name
        else:
            extract_path = await jsl_llm.download_from_s3(llm_name)
            jobs[llm_name] = Status.FINALIZING.value
        await jsl_llm.load_model(
            llm_name=llm_name,
            extract_path_or_remote_name=(extract_path or remote_name),
            device_id=device_id,
            hf_token=hf_token,
        )
    except Exception as ex:
        logger.error("failed to complete job.")
        logger.debug(f"failed to complete job; error={ex}")
        jobs[llm_name] = Status.FAILED.value
        return

    jobs[llm_name] = Status.DEPLOYED.value


async def current_server_info():
    server_info = {
        "system": {
            "torch_cpu_threads": torch.get_num_threads(),
            "is_cuda_available": torch.cuda.is_available(),
            "number_of_cuda_devices": torch.cuda.device_count(),
        },
        "deployment_status": {},
    }
    if gpus := GPUtil.getGPUs():
        gpus_info = []
        for gpu in gpus:
            gpus_info.append(
                {
                    "GPU ID": gpu.id,
                    "GPU Name": gpu.name,
                    "GPU Load": f"{gpu.load * 100 } %",
                    "GPU Memory Free": f"{gpu.memoryFree} MB",
                    "GPU Memory Used": f"{gpu.memoryUsed} MB",
                    "GPU Memory Total": f"{gpu.memoryTotal}  MB",
                    "GPU Temperature": f"{gpu.temperature} °C",
                    "GPU Driver": f"{gpu.driver}",
                }
            )
        server_info["system"]["gpus_info"] = gpus_info

    if jsl_llm.llm:
        server_info["deployment_status"] = {
            "model": jsl_llm.llm_name,
            "status": Status.DEPLOYED.value,
            "device": jsl_llm.device,
            "max_context_length": jsl_llm.model_max_len,
            "deployed_at": jsl_llm.deployed_at,
        }
    elif jobs:
        for llm_name, _status in jobs.items():
            server_info["deployment_status"] = {"model": llm_name, "status": _status}
            if _status in BUSY_STATUS:
                if _status == Status.FINALIZING.value:
                    server_info["deployment_status"]["progress"] = "98 %"
                else:
                    server_info["deployment_status"]["progress"] = (
                        await jsl_llm.get_progress(llm_name)
                    )
            break

    return server_info


@route.get("/status", tags=["System Checks"])
async def server_status():
    return await current_server_info()


@route.get(
    "/info", tags=["System Checks"], summary="Lists available JSL LLMs and their info"
)
async def available_llms_info():
    await jsl_llm.setup_llms_info()
    return {
        llm_name: {"size": info.get("size")}
        for llm_name, info in jsl_llm.llms_info.items()
    }


def check_if_busy():
    if current_status := list(jobs.values()):
        if current_status[0] in BUSY_STATUS:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=Status.JOB_IN_PROGRESS.value,
                headers={"Retry-After": "30s"},
            )
    return False


@route.post("/deploy", tags=["Load/Offload"])
async def deploy_llm(
    data: DeployRequest, bk_task: BackgroundTasks, is_busy=Depends(check_if_busy)
):
    llm_name = data.llm_name
    jobs[llm_name] = Status.STARTING.value
    args = dict(
        llm_name=llm_name,
        device_id=data.device,
        force=data.force,
        hf_token=data.hf_token,
    )
    bk_task.add_task(deployment_task, **args)
    return {"message": Status.DEPLOYMENT_STARTED}


@route.post("/offload", tags=["Load/Offload"])
async def offload_llm(is_busy=Depends(check_if_busy)):
    msg = jsl_llm.offload_model()
    jobs.clear()
    return {"message": msg}


@route.post("/generate", description="Generate prediction", tags=["Generate/Query"])
async def generate_results(data: GenerateRequest, is_busy=Depends(check_if_busy)):
    generation_started = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    start_time = time.perf_counter()
    result = await jsl_llm.get_prediction(
        data.text, data.max_new_tokens, data.temperature
    )
    if type(result) == str:
        return {"message": result}
    output, output_tokens_len = result
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    return {
        "message": output,
        "generation_started": generation_started,
        "time_taken": (
            f"{time_taken* 1000:.3f} ms" if time_taken < 2 else f"{time_taken:.2f} sec"
        ),
        "new_token_generated": output_tokens_len,
        "input": {
            "max_new_tokens": data.max_new_tokens,
            "temperature": data.temperature,
            "prompt_tokens": await jsl_llm.get_input_token_len(data.text),
        },
        "deployment": {
            "deployed_at": jsl_llm.deployed_at,
            "model_name": jsl_llm.llm_name,
            "device": jsl_llm.device,
        },
    }
