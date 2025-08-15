from crewai_tools import FileReadTool
import os
import re

def get_json_tool():
    cur_path = os.getcwd()
    json_folder = cur_path + "/separate_jsons"
    json_files = [f for f in os.listdir(json_folder)]

    for json_filename in json_files:
        json_path = os.path.join(json_folder, json_filename)
        print(f"Processing JSONS: {json_path}")

        current_json_search_tool = FileReadTool(
            file_path=json_path,
        )
        print("current_json_search_tool", current_json_search_tool)
        yield current_json_search_tool

