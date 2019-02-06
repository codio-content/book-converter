import logging
import shutil
import uuid

from pathlib import Path

from converter.toc import get_toc
from converter.guides.tools import slugify, write_file, write_json
from converter.guides.item import CHAPTER
from converter.latex2markdown import LaTeX2Markdown
from converter.assets import copy_assets, convert_assets


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


def cleanup_latex(lines):
    updated = []
    starts = (
        '%', '\\index{', '\\label{', '\\markboth{', '\\addcontentsline{',
        '\\begin{center}', '\\vspace', '\\end{center}', '\\newpage', '\\noindent',
        '\\ttfamily'
    )
    for line in lines:
        if line.startswith(starts):
            continue
        updated.append(line)
    return updated


def make_relative(i, item):
    copied = i.copy()
    copied["position"] = int(copied.get("position")) - item.line_pos
    return copied


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

    pos = 0
    for rule in sorted_rules:
        position = rule.get('position')
        pos += 1
        if position < 0 or position > len(item.lines) + 1:
            logging.info("wrong rule position, it will be ignored %s", rules[pos - 1])
            continue
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


def codio_transformations(toc, transformation_rules):
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


def make_refs(toc):
    refs = {}
    chapter_counter = 0
    section_counter = 0
    exercise_counter = 0
    figs_counter = 0
    chapter_name = None
    is_figure = False
    is_exercise = False

    for item in toc:
        if item.section_type == CHAPTER:
            chapter_counter += 1
            section_counter = 0
            figs_counter = 0
            exercise_counter = 0
            chapter_name = item.section_name
        else:
            section_counter += 1
        for line in item.lines:
            if line.startswith("\\begin{figure}"):
                figs_counter += 1
                is_figure = True
            elif line.startswith("\\end{figure}"):
                is_figure = False
            elif line.startswith("\\begin{exercise}"):
                exercise_counter += 1
                is_exercise = True
            elif line.startswith("\\end{exercise}"):
                is_exercise = False
            elif line.startswith("\\label{"):
                label = line[7:-1]
                refs[label] = {
                    'chapter': chapter_name,
                    'section': item.section_name
                }

                if is_figure:
                    refs[label]["counter"] = '{}.{}'.format(chapter_counter, figs_counter)
                elif is_exercise:
                    refs[label]["counter"] = '{}.{}'.format(chapter_counter, exercise_counter)
                elif item.section_type == CHAPTER:
                    refs[label]["counter"] = '{}'.format(chapter_counter)
                else:
                    refs[label]["counter"] = '{}.{}'.format(chapter_counter, section_counter)

    return refs


def prepare_base_directory(generate_dir, yes=False):
    if generate_dir.exists():
        if not yes:
            name = input("destination directory exists, continue? Y/n: ")
            if name.lower().strip() == 'n':
                return False
        shutil.rmtree(generate_dir, ignore_errors=True)
    return True


def prepare_structure(generate_dir):
    generate_dir.mkdir()
    guides_dir = generate_dir.joinpath(".guides")
    guides_dir.mkdir()
    content_dir = guides_dir.joinpath("content")
    content_dir.mkdir()

    return guides_dir, content_dir


def make_metadata_items(config):
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

    predefined_metadata = config.get('metadata', {})
    metadata = {**metadata, **predefined_metadata}

    return book, metadata


def make_section_items(item, slug_name, md_path, transformation_rules):
    book_item = {
        "id": slug_name,
        "title": item.section_name,
        "type": "chapter" if item.section_type == CHAPTER else "page",
        "pageId": slug_name
    }
    section = {
        "id": slug_name,
        "title": item.section_name,
        "files": [],
        "path": [],
        "type": "markdown",
        "content-file": get_guide_content_path(md_path),
        "chapter": True if item.section_type == CHAPTER else False,
        "reset": [],
        "teacherOnly": False,
        "learningObjectives": ""
    }
    if slug_name in transformation_rules:
        configuration = transformation_rules[slug_name].get('configuration', {})
        if configuration:
            section = {**section, **configuration}

    return section, book_item


def place_section_items():
    pass


def process_assets(config, generate_dir, pdfs_for_convert):
    logging.debug("copy assets")
    copy_assets(config, generate_dir)

    if pdfs_for_convert:
        logging.debug("convert included pdfs")
        convert_assets(config, generate_dir, pdfs_for_convert)


def write_metadata(guides_dir, metadata, book):
    logging.debug("write metadata")

    metadata_path = guides_dir.joinpath("metadata.json")
    book_path = guides_dir.joinpath("book.json")
    write_json(metadata_path, metadata)
    write_json(book_path, book)


def convert(config, base_path, yes=False):
    base_dir = base_path
    generate_dir = base_dir.joinpath("generate")
    if not prepare_base_directory(generate_dir, yes):
        return

    logging.debug("start converting %s" % generate_dir)
    guides_dir, content_dir = prepare_structure(generate_dir)
    transformation_rules = prepare_codio_rules(config)
    toc = get_toc(Path(config['workspace']['directory']), Path(config['workspace']['tex']))
    toc, tokens = codio_transformations(toc, transformation_rules)
    refs = make_refs(toc)
    book, metadata = make_metadata_items(config)

    chapter = None
    current_chapter = None
    chapter_num = 0
    figure_num = 0
    pdfs_for_convert = []
    logging.debug("convert selected pages")

    for item in toc:
        if item.section_type == CHAPTER:
            chapter_num += 1
            figure_num = 0
            slug_name = slugify(item.section_name)
            chapter = item.section_name
        else:
            slug_name = slugify(item.section_name, chapter=chapter)

        logging.debug("convert page %s" % slug_name)

        lines = cleanup_latex(item.lines)

        md_converter = LaTeX2Markdown('\n'.join(lines), refs, chapter_num, figure_num)

        converted_md = md_converter.to_markdown()
        figure_num += md_converter.get_figure_counter()

        if md_converter.get_pdfs_for_convert():
            pdfs_for_convert += md_converter.get_pdfs_for_convert()

        if slug_name in tokens:
            for key, value in tokens.get(slug_name).items():
                converted_md = converted_md.replace(key, value)

        md_path = content_dir.joinpath(slug_name + ".md")
        section, book_item = make_section_items(item, slug_name, md_path, transformation_rules)

        if item.section_type == CHAPTER:
            book_item["children"] = []
            current_chapter = book_item
            book["children"].append(book_item)
        else:
            if current_chapter:
                current_chapter["children"].append(book_item)
            else:
                book["children"].append(book_item)

        metadata["sections"].append(section)

        write_file(md_path, converted_md)

    write_metadata(guides_dir, metadata, book)
    process_assets(config, generate_dir, pdfs_for_convert)
