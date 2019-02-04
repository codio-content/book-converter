import re
import json


def slugify(item, chapter=""):
    name = (chapter + "-" if chapter else "") + item
    return re.sub('[^0-9a-zA-Z]+', '-', name).lower()


def write_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)


def write_json(file_path, json_data):
    write_file(file_path, json.dumps(json_data, sort_keys=True, indent=2, separators=(',', ': ')))


def get_text_in_brackets(line):
    start = line.find('{')
    end = line.rfind('}')
    if start == end or start == -1 or end == -1:
        return line
    return line[start+1:end]
