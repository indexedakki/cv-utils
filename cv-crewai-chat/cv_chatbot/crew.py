# -*- coding: utf-8 -*-
"""
Module: crew.py

Defines the CvChatbot crew, its agents, tasks, and lifecycle hooks.
"""
# pylint: disable=C0412,E1126,E1101

import json
from urllib import response
from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from langchain_openai import ChatOpenAI
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from .tools.custom_tool import MyCustomTool
from .tools.download_link_generator import download_link_generator
from logger_setup import setup_logger

from crewai_tools import RagTool
from .models import candidate_finder, candidate_work_experience, download_link, CVParseResponse
from .config import RAG_CONFIG
rag_tool = RagTool(config=RAG_CONFIG)

# resp1 = rag_tool.run("Akash Kumar")
# print(resp1)

LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)
# Configure the LLM
llm = ChatOpenAI(model="gpt-4o")

@CrewBase
class CvChatbot:
    """
    Crew implementation for a CV-based conversational assistant.
    """

    # Paths to YAML configuration files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # @before_kickoff
    # def pull_data_example(self, inputs: dict) -> dict:
    #     """
    #     Example hook before kickoff: augment inputs with extra data.
    #     """
    #     inputs["extra_data"] = "This is extra data"
    #     return inputs

    # @after_kickoff
    # def log_results(self, output: dict) -> dict:
    #     """
    #     Example hook after kickoff: log and return outputs.
    #     """
        
    

    @agent
    def intent_understanding_agent(self) -> Agent:
        """
        Define the main assistant agent with memory, tools, and delegation.
        """
        return Agent(
            config=self.agents_config["intent_understanding_agent"],
            llm=llm,       
            tools=[rag_tool],         
            allow_delegation=True,
            verbose=True,
            memory=False,
            reasoning=True,
        )

    @agent
    def candidate_finder_agent(self) -> Agent:
        """
        Agent for extracting candidates based on certain criteria.
        """
        return Agent(
            config=self.agents_config["candidate_finder_agent"],
            llm=llm,
            tools=[rag_tool],
            verbose=True,
            memory=False,
            reasoning=True,
            allow_delegation=False,
        )

    @agent
    def work_experience_analysis_agent(self) -> Agent:
        """
        Agent for extracting candidates based on certain criteria.
        """
        return Agent(
            config=self.agents_config["work_experience_analysis_agent"],
            llm=llm,
            tools=[rag_tool],
            verbose=True,
            memory=False,
            reasoning=True,
            allow_delegation=False,
        )
    
    @agent
    def generate_download_link_agent(self) -> Agent:
        """
        Agent for generating responses based on user query.
        """
        return Agent(
            config=self.agents_config["generate_download_link_agent"],
            llm=llm,
            verbose=True,
            memory=False,
            reasoning=True,
            allow_delegation=False,
        )
    
    @agent
    def response_generator_agent(self) -> Agent:
        """
        Agent for generating responses based on user query.
        """
        return Agent(
            config=self.agents_config["response_generator_agent"],
            llm=llm,
            verbose=True,
            memory=False,
            reasoning=True,
            allow_delegation=True,
        )
    
    @task
    def intent_understanding_task(self) -> Task:
        """
        Task for understanding user intent and extracting relevant information.
        """
        return Task(
            config=self.tasks_config["intent_understanding_task"],
            tools=[rag_tool],
            verbose=True,
            memory=False,
            agent=self.intent_understanding_agent()
        )
    
    @task
    def candidate_finder_task(self) -> Task:
        """
        Task for finding candidates based on user intent.
        """
        return Task(
            config=self.tasks_config["candidate_finder_task"],
            tools=[rag_tool],
            verbose=True,
            memory=False,
            context=[self.intent_understanding_task()],
            agent=self.candidate_finder_agent(),
            output_json=candidate_finder
        )
    
    @task
    def work_experience_analysis_task(self) -> Task:
        """
        Task for finding candidates based on user intent.
        """
        return Task(
            config=self.tasks_config["work_experience_analysis_task"],
            tools=[rag_tool],
            verbose=True,
            memory=False,
            context=[self.intent_understanding_task()],
            agent=self.work_experience_analysis_agent(),
            output_json=candidate_work_experience
        )
    
    @task
    def generate_download_link_task(self) -> Task:
        """
        Task for generating download link asked by user.
        """
        return Task(
            config=self.tasks_config["generate_download_link_task"],
            verbose=True,
            memory=False,
            tools=[rag_tool, download_link_generator],
            context=[self.intent_understanding_task()],
            agent=self.generate_download_link_agent(),
            output_json=download_link
        )

    @task
    def response_generator_task(self) -> Task:
        """
        Task for generating responses based on user queries and candidate data.
        """
        return Task(
            config=self.tasks_config["response_generator_task"],
            verbose=True,
            memory=False,
            context=[self.intent_understanding_task(), self.candidate_finder_task(), self.work_experience_analysis_task(), self.generate_download_link_task()],
            agent=self.response_generator_agent(),
            output_json=CVParseResponse
        )

    # def senior_manager(self) -> Agent:
    #     """
    #     Define a manager agent to oversee the crew.
    #     """
    #     return Agent(
    #         role="Senior Manager",
    #         goal="To answer HR-related queries from knowledge base," \
    #         "You should return the same response in the JSON format as received from response_generator_task. The output should only be JSON, nothing else.",
    #         backstory="You are the Senior Manager of the HR department. You have access to a knowledge base containing information about candidates. " \
    #         "You are responsible for answering HR-related queries and generating responses based on the output received from previous tasks.",
    #         llm=llm,
    #         memory=False,
    #         verbose=True,
    #         allow_delegation=True,
    #         reasoning=True,
    #     )
    
    
    @crew
    def crew(self) -> Crew:
        """
        Assemble agents and tasks into a Crew.
        """
        usasge_metrics = {}
        return Crew(
            agents=self.agents,
            tasks=self.tasks,        
            # manager_agent=self.senior_manager(),
            # process="hierarchical",
            verbose=True,
            memory=False,
            usage_metrics=usasge_metrics
        )
