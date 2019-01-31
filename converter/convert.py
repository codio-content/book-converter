import shutil
import json
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
        else:
            slug_name = slugify(section["name"], chapter=chapter)
        rules[slug_name] = section
    return rules


def apply_codio_transformation(lines):
    return lines


def cleanup_latex(lines):
    updated = []
    for line in lines:
        if line.startswith('%'):
            continue
        elif line.startswith('\\index{'):
            continue
        elif line.startswith('\\label{'):
            continue
        elif line.startswith('\\markboth{'):
            continue
        elif line.startswith('\\addcontentsline{'):
            continue
        updated.append(line)
    return updated


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
            chapter = None
            slug_name = slugify(item.section_name, chapter=chapter)
            chapter = item.section_name
        else:
            slug_name = slugify(item.section_name, chapter=chapter)
        print("slug_name", slug_name)
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
