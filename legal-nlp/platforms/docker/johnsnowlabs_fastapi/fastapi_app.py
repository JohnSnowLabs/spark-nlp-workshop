import uvicorn, os
from fastapi import FastAPI, HTTPException
from johnsnowlabs import *
import logging

# Managing logging level
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

# FastAPI object
app = FastAPI()

# Start a Spark NLP Session
jsl.start(exclude_ocr=True)

# Always preload your objects to reduce latency
preloaded = dict()
preloaded['legpipe_deid'] = nlp.PretrainedPipeline('legpipe_deid', 'en', 'legal/models')


# ENDPOINTS
@app.get("/legpipe_deid")
async def get_one_sequential_pipeline_result(text=None):
    if text is None:
        example = """Pizza Fusion Holdings, Inc. Franchise Agreement This Franchise Agreement (the "Agreement") is entered into as of the Agreement Date shown on the cover page between Pizza Fusion Holding, Inc., a Florida corporation, and the individual or legal entity identified on the cover page. Source: PF HOSPITALITY GROUP INC., 9/23/2015t."""
    else:
        example = text

    ann_result = preloaded["legpipe_deid"].fullAnnotate(example)

    result = {}
    for column, ann in ann_result[0].items():
        result[column] = []
        for lines in ann:
            content = {
                "result": lines.result,
                "begin": lines.begin,
                "end": lines.end,
                "metadata": dict(lines.metadata),
            }
            result[column].append(content)
    return result


# FASTAPI start
if __name__ == "__main__":
    uvicorn.run('fastapi_app:app', host='0.0.0.0', port=8515)
