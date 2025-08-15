import os
import json

from logger_setup import setup_logger
LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

def save_json_as_text():
    """
    Convert a JSON object or JSON string to plain text and save it.
    Parameters:
    - json_input: dict or str — the JSON data (as a Python dict/list, or a JSON-formatted string)
    - output_dir: str or Path — directory where you want to save the file
    - filename: str — name of the file (e.g. 'data.txt')
    """

    with open('task_output_resume.json', 'r', encoding='utf-8') as infile:
        data = json.load(infile)
    text = json.dumps(data, ensure_ascii=False, indent=2)
    try:
        with open('cv_parse_runnables/texts/task_output_resume.txt', 'w', encoding='utf-8') as outfile:
            outfile.write(text)
    except Exception as e:
        logger.error(f"Error writing to file: {e}")


def store_extraction_output(task_output, type_of_task):
    """Store the output of the extraction task in a JSON file."""
    if type_of_task == "resume":
        file_path = "task_output_resume.json"
        
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(task_output)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

