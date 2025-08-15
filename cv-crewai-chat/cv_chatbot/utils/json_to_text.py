"""Convert JSON to text file with indentation for nested structures."""
import json
import os
def json_to_lines(obj, indent=0):
    """Recursively convert JSON object to lines of text."""
    lines = []
    pad = '  ' * indent

    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.extend(json_to_lines(v, indent + 1))
            else:
                lines.append(f"{pad}{k}: {v}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.extend(json_to_lines(item, indent + 1))
            else:
                lines.append(f"{pad}- {item}")
    else:
        lines.append(f"{pad}{obj}")

    return lines



def json_to_text():
    """Convert JSON file to text file with indentation for nested structures."""    
    print(os.getcwd())
    with open("cv_chatbot/cv_parsed.json", 'r', encoding='utf-8') as f:
        data = json.load(f)


    # # Generate and print
    # for line in json_to_lines(data):
    #     print(line)


    with open('cv_chatbot/cv_parsed.txt', 'w', encoding='utf-8') as out:
        out.write('\n'.join(json_to_lines(data)))

    # # Convert JSON to lines
    # lines = json_to_lines(data)

    # # Write to output text file
    # output_file = json_file.replace('.json', '.txt')
    # with open(output_file, 'w', encoding='utf-8') as out:
    #     out.write('\n'.join(lines))

    # return output_file
# json_to_text()
