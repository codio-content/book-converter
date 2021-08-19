import csv
import re
import json


def slugify(item, chapter=""):
    name = (chapter + "-" if chapter else "") + item
    return re.sub('[^0-9a-zA-Z]+', '-', name).lower()


def write_file(file_path, content):
    with open(file_path, 'w', encoding="utf-8") as f:
        f.write(content)


def write_json(file_path, json_data, sort_keys=True):
    write_file(file_path, json.dumps(
        json_data, sort_keys=sort_keys, indent=2, separators=(',', ': '), ensure_ascii=False))


def read_file(file_path):
    with open(file_path, 'r', errors='replace', encoding="utf-8") as file:
        return file.read()


def read_file_lines(file_path):
    with open(file_path, 'r', errors='replace', encoding="utf-8") as file:
        return file.readlines()


def get_text_in_brackets(line, start=0):
    start = line.find('{', start)
    end = line.rfind('}')
    if start == end or start == -1 or end == -1:
        return line
    return line[start + 1:end]


def parse_csv_lines(data):
    return [row for row in csv.reader(data.splitlines())]
