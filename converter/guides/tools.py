import re


def slugify(item, chapter=""):
    name = (chapter + "-" if chapter else "") + item
    return re.sub('[^0-9a-zA-Z]+', '-', name).lower()


def write_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)
