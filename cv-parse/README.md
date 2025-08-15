# CV Parsing Agent (CrewAI + FastAPI)

A FastAPI application for CV parsing, orchestrated as an autonomous agent using CrewAI and managed with the lightweight UV dependency manager. The application runs locally via Uvicorn with hot‑reload support and exposes an interactive Swagger UI for testing.

## Prerequisites

- **Git** (to clone the repository)  
- **Python 3.9+**  
- **UV** (dependency & task manager)  
- **OpenAI API Key** (stored in a `.env` file)
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

## Configuration

Create a .env file in the project root with your OpenAI API key:
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
Note: Make sure to keep your .env file secret. Never commit it to your repository.

## Running the Application
Start the FastAPI app with Uvicorn in development mode (hot‑reload enabled):

```bash
uvicorn main:app --reload
```
By default, the server will be available at:
http://127.0.0.1:8000

**Testing via Swagger UI**

http://127.0.0.1:8000/docs

to explore and test all CV parsing endpoints.

## Input & Output

Input: Single or multiple PDF resume files.

Output: A cv_parsed.json file generated in the working directory, containing the parsed CV data.
