from fastapi import Header, File, UploadFile, APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from .resume_parse_utils import process_text, details_

from .additional_logic import additional_data_logic
# from cv_summarise_crews.main import kickoff
from .save_pdfs_to_blob import save_to_blob_with_metadata
from .seperate_json_each_resume import save_json_to_separate_files
from .summarize_jsons import summarize
from .summarize_campaign import summarize_campaign
import fitz

from dotenv import load_dotenv
from typing import List
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_community.callbacks import get_openai_callback
import time
import numpy as np
import uuid
import shutil
import os
import httpx
import asyncio

from logger_setup import setup_logger
LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

logger.info("Starting Resume Ranker API...")

load_dotenv()

router = APIRouter(prefix='/cv_parse', tags=['cv_parse'])
BASE_UPLOAD_DIR = "uploads"

def get_user_folders(user_id: str):
    user_base = os.path.join(BASE_UPLOAD_DIR, user_id)
    cvs_folder = os.path.join(user_base, "cvs")
    os.makedirs(cvs_folder, exist_ok=True)
    return cvs_folder


@router.get("/summarise")
def cv_parser():
    cur_path = os.getcwd()
    os.chdir(cur_path + "/cv_parse_runnables")
    # kickoff()
    os.chdir("..")
    src = cur_path + '/cv_parse_runnables/jsons/task_output_resume.json'
    dst = cur_path + '/task_output_resume.json'
    shutil.copy(src, dst)

@router.post("/ingestion")
async def upload_and_process(
    resumes: List[UploadFile] = File(...),
    user_id: str = None,
    # db: Session = Depends(get_sql_db),
    Authorization: str = Header(None)):
    try:
        shutil.rmtree(os.path.join("cv_parse_runnables", "jsons"))
        shutil.rmtree(os.path.join("cv_parse_runnables", "separate_jsons"))
        shutil.rmtree(os.path.join("cv_parse_runnables", "summaries"))
        shutil.rmtree(os.path.join("cv_parse_runnables", "summaries_campaign"))
        os.remove(os.path.join("task_output_resume.json"))
        logger.info("Folder and contents deleted successfully.")
    except OSError as e:
        logger.exception(f"Error deleting folder: {e}")
    if not user_id:
        user_id = str(uuid.uuid4())
    
    cvs_folder= get_user_folders(user_id)
    # Upload resumes
    for resume in resumes:
        file_uuid = str(uuid.uuid4())
        await save_to_blob_with_metadata(resume, file_uuid)
        resume.file.seek(0)
        resume_path = os.path.join(cvs_folder, resume.filename)
        try:
            with open(resume_path, "wb") as buffer:
                buffer.write(await resume.read())
            doc = fitz.open(resume_path)
            page = doc[0]
            page.insert_text((10, 10),f"Candidate unique identifier-{file_uuid}", fontsize=8)
            doc.save(resume_path, incremental=True, encryption=0)
            doc.close()
        except Exception as e:
            logger.exception(
                f"Error while uploading resume {resume.filename}: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "message":
                    f"Error while uploading resume {resume.filename}: {e}"
                })
        

    current_user = Authorization
    logger.info(f"current user-----> {current_user}")
    li_cvs = os.listdir(cvs_folder)
    results = await invoke({
        'li_cvs': li_cvs,
        'cvs_folder': cvs_folder,
    })


async def invoke(request):
    start_time = time.time()

    async def resume_details_lambda(x):
        return await details_(x['dict_of_cvs_text'])

    input = RunnableParallel({
        "dict_of_cvs_text":
        RunnableLambda(lambda x: process_text(x['li_cvs'], x['cvs_folder'])),
    })
    resume_jd_details = RunnableParallel({
        "resume_details":
        RunnableLambda(resume_details_lambda),
        "dict_of_cvs_text":
        RunnableLambda(lambda x: x["dict_of_cvs_text"])
    })

    chain = input | resume_jd_details
    success_indicator = True
    llm_result = await chain.ainvoke(request)
    final_data = []
    additional_data_logic(final_data)
    save_json_to_separate_files()

    await summarize()
    await summarize_campaign()

    # async with httpx.AsyncClient(timeout=600) as client:
    #     resp = await client.get("http://127.0.0.1:8000/cv_parse/summarise"
    #                             )
    # async with httpx.AsyncClient(timeout=600) as client:
    #     resp = await client.get("http://127.0.0.1:8001/cv_chatbot/store_embeddings")

    try:
        with get_openai_callback() as cb:
            # logger.info(f"get_openai_callback_response: {cb}")
            pass     
    except Exception as e:
        logger.exception(f"Error getting a response from GPT: {e}")
        llm_result = "Error getting a response from GPT. Try again."
        success_indicator = False
        operating_cost = 0.0
        elapsed_time = np.ceil(time.time() - start_time)
        total_tokens = cb.total_tokens
    else:
        if llm_result is not None:
            llm_result = llm_result
            total_tokens = cb.total_tokens
        else:
            llm_result = "GPT could not extract any information."
            success_indicator = False
            operating_cost = 0.0
            elapsed_time = np.ceil(time.time() - start_time)
            total_tokens = total_tokens

    operating_cost = np.round(cb.total_cost, 5)

    end_time = time.time()

    elapsed_time = np.ceil((end_time - start_time))

    logger.info(f"success_indicator: {success_indicator}")
    # logger.info(f"operating_cost: {operating_cost}")
    logger.info(f"end_time: {end_time}")
    logger.info(f"elapsed_time: {elapsed_time}")
    return llm_result, operating_cost, success_indicator, elapsed_time, total_tokens
