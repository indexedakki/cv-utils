# CV Chatbot (CrewAI Agent)

An agentic chatbot powered by CrewAI and OpenAI’s API, designed to handle conversational workflows, fetch contextual data, and execute simple tasks autonomously.

## Table of Contents

- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Running the App](#running-the-app)  
- [Usage](#usage)  
## Features

- **Agentic Workflow**: Chain multiple steps (prompt → action → response) automatically.  
- **CrewAI Integration**: Leverage CrewAI’s planning and execution engine for complex tasks.  
- **OpenAI API**: Natural language understanding and generation.  
- **Lightweight**: Managed with [uv](https://github.com/indygreg/uv) for dependencies and task running.

## Prerequisites

- **Python 3.9+**  
- **Git**  
- **UV** (dependency & task manager)  
- **OpenAI API Key**  
- **Microsoft Visual Studio Build Tools with C++ Desktop development**
## Installation

1. **Download Microsoft Visual Studio Build Tools and install Desktop development with C++.**
   
2. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/cv_chatbot.git
   cd cv_chatbot
    ```

3. **Install and lock dependencies**

   ```bash
   uv sync 
   ```

Let's create wonders together with the power and simplicity of crewAI.

## Configuration
Create a .env file in the project root with your OpenAI API key:
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
Note: Make sure to keep your .env file secret. Never commit it to your repository.

## Running the App
Start the chatbot agent with:

```bash
uv run cv_chatbot
```
This will launch the agent in interactive mode. It will read your input, plan actions via CrewAI, call the OpenAI API, and respond.

## Usage
Interactive Mode
After running uv run cv_chatbot, type your questions or commands at the prompt.

**Example**

> Compare all the candidates and their skill in a table.
The agent will:

Plan steps (e.g., locate report, parse data, summarize).

Execute each step via CrewAI and OpenAI.

Return a structured summary.
