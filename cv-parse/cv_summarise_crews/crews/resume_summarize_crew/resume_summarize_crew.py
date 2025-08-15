from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import JSONSearchTool, PDFSearchTool, FileReadTool
from langchain_community.tools.gmail.get_thread import GmailGetThread
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from pathlib import Path

import re
import os

from logger_setup import setup_logger
LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

def store_extraction_output(task_output):
    """Store the output of the extraction task in a Txt file."""
    if not os.path.exists("summaries"):
        logger.info("Creating directory 'summaries'.")
        os.makedirs("summaries", exist_ok=True)
    try:
        m = re.search(r"Candidate\s*Name:\s*(?P<name>.*?)(?=\s*Location:)", str(task_output))
        if m:
            name = m.group(1).strip()
        print("Current dir -------------> ", os.getcwd())
        file_path = f"summaries/{name}.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(task_output))
        print(f"Extraction output stored in {file_path}")
    except Exception as e:
        logger.error(f"Name could not be extracted from summary: {e}")


@CrewBase
class ResumeParserCrew:
    """CvRanker crew"""

    def __init__(self, get_current_json: FileReadTool):
        self.get_current_json = get_current_json
        logger.info(f"Search tool initialized: ")

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    llm = ChatOpenAI(model="gpt-4o")

    @after_kickoff
    def log_results(self, output: dict) -> dict:
        """
        Example hook after kickoff: log and return outputs.
        """
        print(f"Results: {output}")
        return output
    
    @agent
    def resume_summarizer_agent(self) -> Agent:
        return Agent(config=self.agents_config['resume_summarizer_agent'],
                     tools=[self.get_current_json],
                     verbose=True,
                     allow_delegation=True,
                     llm=self.llm
                     )

    @task
    def resume_summarizer_task(self) -> Task:
        return Task(config=self.tasks_config['resume_summarizer_task'],
                    tools=[self.get_current_json],
                    verbose=True,
                    callback=store_extraction_output)

    @crew
    def crew(self) -> Crew:
        """Creates the Email Filter Crew"""
        usasge_metrics = {}
        execution_logs = []
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            # cache=True,
            # memory=True,
            usage_metrics=usasge_metrics)
