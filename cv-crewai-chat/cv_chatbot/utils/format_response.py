from crewai import LLM
llm = LLM(model="gpt-4o")

import json

from logger_setup import setup_logger
LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

def type_check(input):
    prompt = f"""Please see whether "Question : {input}" 
        If it is related to candidates or skills, return 1
        Sample questions:
        "show me candidates with experience in data engineering"
        "show me candidates with skills in python"
        
        If it is related to work experience, return 2
        "show me work experience of candidates with skills in python"

        If it is related to asking for resume or downloading resume, return 3
        "show me resume of Rahul"

        else return 0
        
        "Your response should be only a number, either 0, 1, 2, 3"""          
    response = llm.call(
        messages=[
            {"role": "user", "content": prompt}
        ],   
        )
    llm_output = response
    logger.info(f"Type check: {llm_output}")
    return llm_output

def format_response(output, type_check):
    # try:  
        if type_check == "1":
            final_response = output["candidate"]
        elif type_check == "2":
            final_response = output["work_experience"]
        elif type_check == "3":
            final_response = output["download_link"]
        else:
            final_response = output["response_message"]

        logger.info(f"Final Response: {final_response}")
        return final_response
    # except Exception as e:
    #     logger.error(f"Error in decoding json: {e}")