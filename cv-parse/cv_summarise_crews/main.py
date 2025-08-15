import os
import time
from typing import List
import tracemalloc
import psutil
import asyncio
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
from cv_summarise_crews.crews.resume_summarize_crew.resume_summarize_crew import ResumeParserCrew
from cv_summarise_crews.utils.json_rag_search import get_json_tool
from cv_summarise_crews.utils.calculate_openai_cost import openai_cost
# from cv_summarise_crews.utils.seperate_json_each_resume import save_json_to_separate_files
from cv_summarise_crews.utils.save_summary_to_blob import save_to_blob


from logger_setup import setup_logger
LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

logger.info("Starting CV Ranker Flow...")

os.environ["CREWAI_STORAGE_DIR"] = r"C:\crew_data"

class cv_ranker_state(BaseModel):
    """ State for CV ranking """
    # Define the state attributes here
    parsed_result: None = None
    crew_instance: None = None
    
class cv_ranker_flow(Flow[cv_ranker_state]):
    """ Application flow for CV ranking """
    @start("wait_next_run")
    async def summarise(self):
        start_time = time.time()
        logger.info("Starting the CV Ranker Flow")
        final_data = []  
        all_usage_metrics = []

        save_json_to_separate_files()

        tools = await asyncio.to_thread(get_json_tool)
        async with asyncio.TaskGroup() as tg:
            for tool in tools:
                tg.create_task(self._process_tool(tool, final_data, all_usage_metrics))

        end_time = time.time()
        duration = end_time - start_time
        logger.info("CV Ranker Flow completed in %.2f seconds", duration)

        logger.info("Usasge metrics:")
        total_prompt_tokens = sum(m.prompt_tokens for m in all_usage_metrics)
        total_completion_tokens = sum(m.completion_tokens for m in all_usage_metrics)
        total_successful_requests = sum(m.successful_requests for m in all_usage_metrics)
        total_cached_prompt_tokens = sum(m.cached_prompt_tokens for m in all_usage_metrics)

        openai_cost(total_prompt_tokens, total_cached_prompt_tokens, total_completion_tokens, total_successful_requests)
        
        return self.state.parsed_result
    
    async def _process_tool(self, tool, final_data, all_usage_metrics):
        current_start = time.time()

        self.state.parsed_result = await asyncio.to_thread(ResumeParserCrew, tool)
        self.state.crew_instance = await asyncio.to_thread(self.state.parsed_result.crew)
        await asyncio.to_thread(self.state.crew_instance.kickoff)
        
        all_usage_metrics.append(self.state.crew_instance.usage_metrics)
        current_duration = time.time() - current_start
        logger.info("Current resume parsed in %.2f seconds", current_duration)

    @listen(summarise)
    def save_summaries(self):
        save_to_blob()

def kickoff():
    """
    Run the flow.
    """

    tracemalloc.start()
    process = psutil.Process(os.getpid()) 
    logger.info("Kickoff called")

    cv_rank_flow = cv_ranker_flow()
    cv_rank_flow.kickoff()

    current, peak = tracemalloc.get_traced_memory()
    logger.info(f"Python alloc current: {current / (1024**2):.2f} MB")
    logger.info(f"Python alloc peak:    {peak / (1024**2):.2f} MB")

    rss_mb = process.memory_info().rss / (1024**2)
    logger.info(f"Process RSS:          {rss_mb:.2f} MB")
    tracemalloc.stop()


def plot():
    """
    Plot the flow.
    """
    logger.info("Plot called")
    cv_rank_flow = cv_ranker_flow()
    cv_rank_flow.plot()
