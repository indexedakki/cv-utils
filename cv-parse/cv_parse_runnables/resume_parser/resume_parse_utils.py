from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import ChatOpenAI
import os
from .prompt_template import *
from dotenv import load_dotenv
from pdfminer.high_level import extract_text
import asyncio
from .store_output import store_extraction_output
import json

load_dotenv()

from logger_setup import setup_logger
LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    seed=42
    )


def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    print(text)
    return text


def process_text(li_docs,folder_path):
    try:
        with ThreadPoolExecutor() as cvs_executor, ThreadPoolExecutor() as jds_executor:
            text = {cvs_executor.submit(extract_text_from_pdf, f'{folder_path}/{pdf}'): pdf for pdf in li_docs}

            dict_of_text = {}
            for future in as_completed(text):
                pdf = text[future]
                try:
                    details = future.result()
                    dict_of_text[pdf] = details
                    logger.info(f"Extracted text from pdf: {pdf}")
                except Exception as e:
                    logger.info(f"Error extracting details from {pdf}: {e}")

        return dict_of_text
    
    except Exception as e:
        logger.info(f"Error while processing {li_docs}")


async def details_(dict_of_resume_text):
    resume_details = {}
    
    async def process_resume_wrapper(text, filename):
        return await process_resume(text, filename)

    async with asyncio.TaskGroup() as tg:
        tasks = {
            tg.create_task(process_resume_wrapper(text, filename)): filename
            for filename, text in dict_of_resume_text.items()
        }

    for task in tasks:
        filename = tasks[task]
        try:
            details = await task
            resume_details[filename] = details
            logger.info(f"Extracted JSON Data from file: {filename}")

            # print(f"details: {details}")
        except Exception as e:
            logger.error(f"Error extracting details from {filename}: {e}")

    return resume_details

async def process_resume(text, filename):    
    parser = JsonOutputParser(pydantic_object=resume)

    prompt = PromptTemplate(
        template=resume_template,
        input_variables=["resume"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser

    result_resume: str = await chain.ainvoke({"resume":text})
    json_text = json.dumps(result_resume)
    final_json = json.loads(json_text)

    store_extraction_output(final_json, "resume")

    logger.info(f'Output stored for file: {filename}')
    return result_resume