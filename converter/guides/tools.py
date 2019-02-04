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
