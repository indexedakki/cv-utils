import os, re, json
from logger_setup import setup_logger
LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)

def save_json_to_separate_files():
    output_dir = "cv_parse_runnables/separate_jsons"
    os.makedirs(output_dir, exist_ok=True)
    try:
        with open('cv_parse_runnables/jsons/task_output_resume.json', 'r',
                    encoding='utf-8') as infile:
            data = json.load(infile)
        # data[0] is the inner list of person-dicts
        for person in data[0]:
            # Safely extract name and build a filename
            name = person.get("Personal_Details", {}).get("Name", "unknown")
            safe_name = name.strip().replace(" ", "_")
            filename = f"{safe_name}.json"
            full_path = os.path.join(output_dir, filename)

            # Write the single-person dict to its own file
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(person, f, ensure_ascii=False, indent=4)

            logger.info(f"Saved {name} to {full_path}")
    except Exception as e:
        logger.error(f"Error saving JSON files for file {name}: {e}")