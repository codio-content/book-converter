import logging
import subprocess
import re
import uuid
import shutil

from argparse import ArgumentParser
from os import listdir
from pathlib import Path
from collections import namedtuple

from converter.weteach2markdown import normalize_output
from converter.guides.tools import write_file, write_json

DocumentsToProcess = namedtuple('DocumentsToProcess', ['base_dir', 'name', 'doc'])


def sort_processing_items_key(item):
    """
    Topic_1.1
    Topic_1.2
    ...
    Unit_1_Project
    Topic_2.1
    Topic_2.2
    ...
    Unit_2_Project
    ....
    Unit_N_Project
    """
    parts = item.name.split('_')
    sub_num = int(float(parts[1]) * 1000)
    if item.name.startswith('Unit'):
        sub_num += 999
    sub_pre = parts[-1]
    if sub_pre.isalpha():
        return f'{sub_num}{sub_pre}'
    return f'{sub_num}'


def sort_processing_items(items):
    return sorted(items, key=sort_processing_items_key)


def convert(base_directory, output):
    print('output', output)
    to_process = []
    for f_item in listdir(base_directory):
        sub_content = base_directory.joinpath(f_item)
        if sub_content.is_dir():
            for file in Path(sub_content).rglob('*.md'):
                if not file.name.startswith('~'):
                    to_process.append(DocumentsToProcess(sub_content, f_item, file))

    sorted_items = sort_processing_items(to_process)

    structure = []
    sections = []

    for element in sorted_items:
        convert_md(element, output, structure, sections)

    guides_dir = output.joinpath('.guides')
    book_file = guides_dir.joinpath('book.json')
    write_json(book_file, full_book_structure(structure))

    updated_sections = list(map(lambda section: write_section_files(section, output), sections))

    metadata_file = guides_dir.joinpath('metadata.json')
    write_json(metadata_file, full_metadata(updated_sections))


def write_section_files(section, output_dir):
    name = section['id']
    content_file = output_dir.joinpath('.guides/content').joinpath(f'{name}.md')
    content_file.parent.mkdir(parents=True, exist_ok=True)
    relative_path = content_file.relative_to(output_dir)
    additional = section.get('content-file-additional', '')
    base_content = section.get('content-file', '')
    content = f'{base_content}\n\n\n{additional}'
    write_file(content_file, content)
    section['content-file'] = str(relative_path)
    if additional:
        del section['content-file-additional']
    return section


def full_book_structure(structure):
    return {
        "name": "We Teach CS",
        "children": structure
    }


def full_metadata(structure):
    return {
        "theme": "light",
        "scripts": [],
        "lexikonTopic": "",
        "useSubmitButtons": True,
        "useMarkAsComplete": True,
        "sections": structure
    }


def slugify(in_str):
    return re.sub('[^a-zA-Z0-9]+', '', in_str).lower()


def prepare_page_name(name):
    separated = re.sub('([A-Z])', ' \\1', name).strip().replace('--', '')
    slugified = re.sub('[^a-zA-Z0-9]+', '', name).replace('PartA', '').replace('PartB', '')
    return separated, slugified


def book_item(name, item_type, has_children):
    generated_item = {
        "id": slugify(name),
        "title": name,
        "type": item_type
    }
    if has_children:
        generated_item['children'] = []
    else:
        generated_item['pageId'] = slugify(name)
    return generated_item


def section_item(name, files):
    return {
        "id": slugify(name),
        "title": name,
        "files": files,
        "path": [],
        "type": "markdown",
        "content-file": "",
        "chapter": False,
        "reset": [],
        "teacherOnly": False,
        "learningObjectives": "",
        "layout": "3-cell"
    }


def read_md(file):
    with open(file, 'r', errors='replace') as file:
        content = file.readlines()
        return '\n'.join(content)


def convert_md(element, output_dir, structure, sections):
    utf8_output = read_md(element.doc)

    unit_name, topic_name, normalized_output = normalize_output(utf8_output, str(output_dir))

    result = re.match(r"(.*)Unit\s(\d+)\s(Lab\s|Labs\s)?[\-]+(?P<uname>[a-zA-Z0-9\s]+)", unit_name)
    uname = 'Unit ' + result.group(2) + ' -- ' + result.group('uname').strip()
    tname = ''

    if topic_name:
        result = re.match(r"(.*)(Topic|Topics)\s(\d)(?P<tname>.*)", topic_name)
        tname = (result.group(2) + ' ' + result.group(3) + result.group(4)).rstrip('*').replace('--', '-')

    if not tname:
        uname = unit_name.strip('*')

    if unit_name == topic_name:
        uname = uname.replace(tname, '')

    uname = uname.lstrip('>').lstrip('#').strip().rstrip('-').strip()\
        .replace(' Lab', '').replace(' Classes Topics', ' Classes').replace('--', '-')

    print('uname', uname)

    book_item_unit = book_item(uname, "chapter", True)

    top_item = next((item for item in structure if item['title'] == book_item_unit['title']), None)
    if not top_item:
        top_item = book_item_unit
        structure.append(book_item_unit)

    book_item_topic = book_item(tname, "section", True)

    if tname:
        top_item['children'].append(book_item_topic)
        top_item = book_item_topic

    current_content = []
    current_item = None

    for line in normalized_output.split('\n'):
        result = re.match(r"(.*)(\d)+\.(\d|[ABCDS])+\.(\d|[ABCDS])+\s[\-]+", line)
        if not result:
            current_content.append(line)
            continue

        line_strip = line.lstrip('*').strip()
        result_sp = re.match(
            r"(Lab )?(\d\.)?(\d)+\.(\d|[ABCDS])+\.(\d|[ABCDS])+\s[\-]+\s?([a-zA-Z\s\-0-9]+)(\*\*)?.*", line_strip
        )
        if not result_sp:
            current_content.append(line)
            continue

        if current_item:
            current_item['content-file'] = '\n'.join(current_content)
            sections.append(current_item)
            current_content = []

        prefix = result_sp.group(2) if result_sp.group(2) else ''
        ex_name = result_sp.group(6).rstrip('--').strip()
        title = prefix + result_sp.group(3) + '.' + result_sp.group(4) + '.' + \
            result_sp.group(5) + ' ' + ex_name

        label, file = prepare_page_name(ex_name)

        file_to_open = str(process_starter_files(f'{file}.java', output_dir, tname or uname, element.base_dir))
        file_to_open = file_to_open.replace(str(output_dir), '').lstrip('/')
        base_ex_dir = Path(file_to_open).parent

        run_content = f"{{Compile and Run | terminal}}(javac {file_to_open} && java -cp {base_ex_dir} {file} )"
        solution_file_content = process_solution_files(f'{file}.java', element.base_dir)
        solution_content = ''
        if solution_file_content:
            solution_content = f"""
|||guidance
## Solution (only visible to teacher)
```java
{solution_file_content}
```
|||
"""

        files = [
            {
                "path": "#tabs",
                "action": "close"
            },
            {
                "path": file_to_open,
                "panel": 0,
                "action": "open"
            },
            {
                "path": "#terminal: clear;",
                "panel": 1,
                "action": "open"
            }
        ]

        book_item_lab = book_item(title, "page", False)

        if ex_name in line:
            sub_position_file = line.index(ex_name)
            if '-' in line[sub_position_file:]:
                sub_position_delimetr = line.index('-', sub_position_file)
                if sub_position_delimetr > -1:
                    sub_content = line[sub_position_delimetr + 1:]
                    sub_content = sub_content.strip().strip('-').strip('*').strip('-').strip()
                    if sub_content:
                        current_content.append(sub_content)

        top_item['children'].append(book_item_lab)
        current_item = section_item(title, files)
        current_item['content-file-additional'] = f'{run_content}\n{solution_content}'

    if current_item:
        current_item['content-file'] = '\n'.join(current_content)
        sections.append(current_item)
    elif not tname:
        top_item['pageId'] = slugify(uname)
        files = [
            {
                "path": "#tabs",
                "action": "close"
            },
            {
                "path": "#terminal: clear;",
                "panel": 1,
                "action": "open"
            }
        ]
        book_item_unit['type'] = 'page'
        del book_item_unit['children']
        current_item = section_item(uname, files)
        current_item['content-file'] = '\n'.join(current_content)
        sections.append(current_item)


def process_solution_files(file_name, base_dir):
    solution_file = base_dir.joinpath('source_code/Solutions').joinpath(file_name)
    if not solution_file.exists():
        return ""
    with open(solution_file, 'r', errors='replace') as file:
        content = file.readlines()
        return '\n'.join(content)


def process_starter_files(file_name, output_dir, topic_name, base_dir):
    starters_file = base_dir.joinpath('source_code/Starters').joinpath(file_name)
    dst_file = output_dir.joinpath('files').joinpath(slugify(topic_name)).joinpath(file_name)
    content = []
    if starters_file.exists():
        with open(starters_file, 'r', errors='replace') as file:
            content = file.readlines()
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    write_file(dst_file, '\n'.join(content))
    return dst_file


def prepare(base_directory, output):
    shutil.rmtree(output, ignore_errors=True)
    to_process = []
    for f_item in listdir(base_directory):
        sub_content = base_directory.joinpath(f_item)
        if sub_content.is_dir():
            for file in Path(sub_content).rglob('*.docx'):
                if not file.name.startswith('~'):
                    to_process.append(DocumentsToProcess(sub_content, f_item, file))

    for element in to_process:
        docx_to_markdown(element, output)


def docx_to_markdown(element, output_dir):
    media_dir = output_dir.joinpath('.guides').joinpath('media').joinpath(str(uuid.uuid4())).absolute()
    command = ['pandoc', '--extract-media', str(media_dir), '--wrap=none', '-t', 'markdown', element.doc]
    result = subprocess.run(command, capture_output=True)
    utf8_output = result.stdout.decode('utf-8')
    unit_name, topic_name, normalized_output = normalize_output(utf8_output, str(output_dir), skip_names=False)

    md_file = str(element.doc).replace('.docx', '.md')

    write_file(md_file, normalized_output)


def main():
    parser = ArgumentParser(description='Process weteach-cs docs to codio guides.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+', help='path to a sources directory')
    parser.add_argument('-l', '--log', action='store', default=None)
    parser.add_argument('--output', type=str, help='path to output folder')
    parser.add_argument('--prepare', help='prepare markdown structure', default=False, action='store_true')

    args = parser.parse_args()

    logging.basicConfig(filename=args.log, level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname).5s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    if args.prepare:
        for path in args.paths:
            prepare(Path(path), Path(args.output))
    else:
        for path in args.paths:
            convert(Path(path), Path(args.output))


if __name__ == '__main__':
    main()
