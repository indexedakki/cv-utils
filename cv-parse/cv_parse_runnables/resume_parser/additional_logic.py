from datetime import datetime
from dateutil import relativedelta
import json
import os

from logger_setup import setup_logger
LOG_PATH = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)


def calculate_months_worked(professional_details):
    try:
        results = []
        all_company_total_months = 0
        current_len_of_professional_details = 1

        for job in professional_details:
            start_date_str = job.get("start_date")
            end_date_str = job.get("end_date")
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            except (TypeError, ValueError):
                logger.error(f"Invalid or missing start date: {start_date_str}")
                continue
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                except ValueError:
                    logger.error(
                        f"Invalid end date: {end_date_str} Using current date instead."
                    )
                    end_date = datetime.today()
            else:
                end_date = datetime.today()
            delta = relativedelta.relativedelta(end_date, start_date)
            total_months = delta.years * 12 + delta.months
            all_company_total_months += total_months
            avg_duration = all_company_total_months // current_len_of_professional_details
            current_len_of_professional_details += 1
            results.append({
                "employer_name": job.get("employer_name"),
                "job_title": job.get("job_title"),
                "months_worked": total_months,
                "avg_duration": avg_duration
            })

        return results
    except Exception as e:
        logger.error(f"Error while calculating months worked")


def detect_career_gaps(professional_details, gap_threshold_months=1):
    try:
        jobs = []
        for job in professional_details:
            start_date_str = job.get("start_date")
            end_date_str = job.get("end_date")
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            except (TypeError, ValueError):
                logger.error(f"Invalid or missing start date: {start_date_str}")
                continue
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                except ValueError:
                    logger.error(f"Invalid end date: {end_date_str}")
                    continue
            else:
                end_date = datetime.today()

            jobs.append({
                "employer_name": job.get("employer_name"),
                "job_title": job.get("job_title"),
                "start_date": start_date,
                "end_date": end_date
            })
        jobs.sort(key=lambda x: x["start_date"])
        gaps = []
        for i in range(1, len(jobs)):
            previous_end = jobs[i - 1]["end_date"]
            current_start = jobs[i]["start_date"]
            gap = relativedelta.relativedelta(current_start, previous_end)
            gap_months = gap.years * 12 + gap.months
            if gap_months > gap_threshold_months:
                gaps.append({
                    "gap_duration_months": gap_months,
                    "between": {
                        "previous_employer": jobs[i - 1]["employer_name"],
                        "next_employer": jobs[i]["employer_name"]
                    }
                })

        return gaps
    except Exception as e:
        logger.error(f"Error while calculating career gap")


def additional_data_logic(final_data):
    try:
        cur_path = os.getcwd()
        file_path = cur_path + "/task_output_resume.json"
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
        if isinstance(data, dict):
            data = [data]


        for i in range(len(data)):
            professional_details = data[i]["Professional_Experience"]
            professional_details = professional_details
            months_worked = calculate_months_worked(professional_details)

            data[i]["avg_duration_in_company"] = months_worked
            gaps = detect_career_gaps(professional_details)
            data[i]["career_gap"] = gaps

        # data = data[-1]
        final_data.append(data)
        with open(file_path, 'w') as file:
            json.dump(final_data, file, indent=4)

        logger.info("Avg duration and Career gap computed successfully!")
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(f"Error for candidate {data[i]['Personal_Details']['Name']}")

    save_json_to_cv_parse_runnables(final_data)


def save_json_to_cv_parse_runnables(data):
    cur_path = os.getcwd()
    file_path = os.path.join(cur_path, "cv_parse_runnables", "jsons",
                             "task_output_resume.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

    if os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
