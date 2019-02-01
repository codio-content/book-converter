import shutil
import json
import uuid
from pathlib import Path

from converter.toc import get_toc
from converter.guides.tools import slugify, write_file
from converter.guides.item import CHAPTER
from converter.latex2markdown import LaTeX2Markdown


def get_guide_content_path(file_path):
    file_path = str(file_path)
    pos = file_path.find(".guides")
    if pos == -1:
        return file_path
    return file_path[pos:]


def prepare_codio_rules(config):
    chapter = None
    rules = {}
    for section in config["sections"]:
        if section["type"] == CHAPTER:
            slug_name = slugify(section["name"])
            chapter = section["name"]
        else:
            slug_name = slugify(section["name"], chapter=chapter)
        rules[slug_name] = section
    return rules


def apply_codio_transformation(lines):
    return lines


def cleanup_latex(lines):
    updated = []
    starts = (
        '%', '\\index{', '\\label{', '\\markboth{', '\\addcontentsline{',
        '\\begin{center}', '\\vspace', '\\end{center}', '\\newpage', '\\noindent'
    )
    for line in lines:
        if line.startswith(starts):
            continue
        updated.append(line)
    return updated


def make_relative(i, item):
    i["position"] = int(i.get("position")) - item.line_pos
    return i


def modify_rules_position(rules, start_position, delta):
    for rule in rules:
        position = rule.get('position')
        if position < start_position:
            continue
        rule['position'] = rule['position'] + delta


def apply_codio_rules_to_item(item, rules):
    relative = map(lambda i: make_relative(i, item), rules)
    sorted_rules = sorted(relative, key=lambda i: i.get("position"))

    tokens = {}

    for rule in sorted_rules:
        position = rule.get('position')
        if position < 0 or position > len(item.lines) + 1:
            print("wrong rule position, it will be ignored", rule)
            continue
        print("-" * 20)
        print("item", item.lines)
        if 'add' in rule:
            text = rule.get('add')
            token = str(uuid.uuid4())
            tokens[token] = text
            item.lines.insert(position, token)
            modify_rules_position(sorted_rules, position, 1)
        if 'remove' in rule:
            count = rule.get('remove', 1)
            for _ in range(count):
                item.lines.pop(position)
            modify_rules_position(sorted_rules, position, 0 - count)

    return tokens


def codio_transformations(toc, config):
    transformation_rules = prepare_codio_rules(config)
    updated_toc = []
    chapter = None
    tokens = {}

    for item in toc:
        if item.section_type == CHAPTER:
            slug_name = slugify(item.section_name)
            chapter = item.section_name
        else:
            slug_name = slugify(item.section_name, chapter=chapter)

        if slug_name in transformation_rules:
            rules = transformation_rules[slug_name].get("transformations")
            if isinstance(rules, str) and rules == "skip":
                continue
            elif isinstance(rules, list) and rules:
                tokens[slug_name] = apply_codio_rules_to_item(item, rules)

        updated_toc.append(item)

    return updated_toc, tokens


def convert(config, base_path):
    base_dir = base_path
    generate_dir = base_dir.joinpath("generate")
    if generate_dir.exists():
        name = input("destination directory exists, continue? Y/n: ")
        if name.lower().strip() == 'n':
            return
        shutil.rmtree(generate_dir, ignore_errors=True)
    generate_dir.mkdir()
    guides_dir = generate_dir.joinpath(".guides")
    guides_dir.mkdir()
    content_dir = guides_dir.joinpath("content")
    content_dir.mkdir()
    toc = get_toc(Path(config['workspace']['directory']), Path(config['workspace']['tex']))

    toc, tokens = codio_transformations(toc, config)

    print('tokens', tokens)

    chapter = None

    book = {
        "name": "TODO: book name",
        "children": []
    }
    metadata = {
        "sections": [],
        "theme": "light",
        "scripts": [],
        "lexikonTopic": "",
        "suppressPageNumbering": False,
        "useSubmitButtons": True,
        "useMarkAsComplete": True,
        "hideMenu": False,
        "allowGuideClose": False,
        "collapsedOnStart": False,
        "hideSectionsToggle": False,
        "hideBackToDashboard": False,
        "protectLayout": False
    }

    current_chapter = None

    for item in toc:
        if item.section_type == CHAPTER:
            slug_name = slugify(item.section_name)
            chapter = item.section_name
        else:
            slug_name = slugify(item.section_name, chapter=chapter)

        book_item = {
            "id": slug_name,
            "title": item.section_name,
            "type": "chapter" if item.section_type == CHAPTER else "page",
            "pageId": slug_name
        }
        if item.section_type == CHAPTER:
            book_item["children"] = []
            current_chapter = book_item
            book["children"].append(book_item)
        else:
            if current_chapter:
                current_chapter["children"].append(book_item)
            else:
                book["children"].append(book_item)

        lines = apply_codio_transformation(item.lines)
        lines = cleanup_latex(lines)

        md_converter = LaTeX2Markdown('\n'.join(lines))
        converted_md = md_converter.to_markdown()

        if slug_name in tokens:
            for key, value in tokens.get(slug_name).items():
                converted_md = converted_md.replace(key, value)

        md_path = content_dir.joinpath(slug_name + ".md")
        section = {
            "id": slug_name,
            "title": item.section_name,
            "files": [],
            "path": [],
            "type": "markdown",
            "content-file": get_guide_content_path(md_path),
            "chapter": False,
            "reset": [],
            "teacherOnly": False,
            "learningObjectives": ""
        }
        metadata["sections"].append(section)
        write_file(md_path, converted_md)

    metadata_path = guides_dir.joinpath("metadata.json")
    book_path = guides_dir.joinpath("book.json")
    write_file(metadata_path, json.dumps(metadata, sort_keys=True, indent=2, separators=(',', ': ')))
    write_file(book_path, json.dumps(book, sort_keys=True, indent=2, separators=(',', ': ')))
