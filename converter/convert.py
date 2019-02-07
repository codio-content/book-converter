import logging
import shutil
import uuid

from pathlib import Path

from converter.toc import get_toc
from converter.guides.tools import slugify, write_file, write_json
from converter.guides.item import SectionItem, CHAPTER
from converter.latex2markdown import LaTeX2Markdown
from converter.assets import copy_assets, convert_assets, process_source_code
from converter.refs import make_refs, override_refs, get_ref_chapter_counter_from


def get_guide_content_path(file_path):
    file_path = str(file_path)
    pos = file_path.find(".guides")
    if pos == -1:
        return file_path
    return file_path[pos:]


def prepare_codio_rules(config):
    chapter = None
    rules = {}
    sections = config.get('sections', list())
    for section in sections:
        if section["type"] == CHAPTER:
            slug_name = slugify(section["name"])
            chapter = section["name"]
        else:
            slug_name = slugify(section["name"], chapter=chapter)
        section["slug"] = slug_name
        rules[slug_name] = section

    insert_rules = {}
    insert_sections = config.get('insert_sections', [])
    for section in insert_sections:
        position = slugify(section["section"], chapter=section["chapter"])
        section["position"] = position
        insert_rules.setdefault(position, []).append(section)

    return rules, insert_rules


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


def generate_insert_items(insert_rules, slug_name):
    inserts_before = []
    inserts_after = []
    if slug_name in insert_rules:
        rules = insert_rules[slug_name]
        for rule in rules:
            insert_item = SectionItem(section_name=rule.get('name'), section_type=rule.get('type'), line_pos=1)
            latex = rule.get('latex')
            markdown = rule.get('markdown')
            before = rule.get('before', False)
            insert_item.codio_section = rule.get('codio_section')
            if latex:
                insert_item.lines = latex.split('\n')
            elif markdown:
                insert_item.markdown = markdown
            else:
                continue
            if before:
                inserts_before.append(insert_item)
            else:
                inserts_after.append(insert_item)
    return inserts_before, inserts_after


def codio_transformations(toc, transformation_rules, insert_rules):
    updated_toc = []
    chapter = None
    tokens = {}

    for item in toc:
        if item.section_type == CHAPTER:
            slug_name = slugify(item.section_name)
            chapter = item.section_name
        else:
            slug_name = slugify(item.section_name, chapter=chapter)

        skip = False

        if slug_name in transformation_rules:
            rules = transformation_rules[slug_name].get("transformations")
            codio_section = transformation_rules[slug_name].get('codio_section', None)
            if codio_section:
                item.codio_section = codio_section
            if isinstance(rules, str) and rules == "skip":
                skip = True
            elif isinstance(rules, list) and rules:
                tokens[slug_name] = apply_codio_rules_to_item(item, rules)

        inserts_before, inserts_after = generate_insert_items(insert_rules, slug_name)

        if inserts_before:
            updated_toc += inserts_before

        if not skip:
            updated_toc.append(item)

        if inserts_after:
            updated_toc += inserts_after

    return updated_toc, tokens


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


def get_section_type(item):
    if item.codio_section == "start":
        return "section"
    return "chapter" if item.section_type == CHAPTER else "page"


def make_section_items(item, slug_name, md_path, transformation_rules):
    book_item = {
        "id": slug_name,
        "title": item.section_name,
        "type": get_section_type(item),
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


def process_assets(config, generate_dir, pdfs_for_convert, source_codes):
    logging.debug("copy assets")
    copy_assets(config, generate_dir)

    if pdfs_for_convert:
        logging.debug("convert included pdfs")
        convert_assets(config, generate_dir, pdfs_for_convert)

    if source_codes:
        logging.debug("process source codes")
        process_source_code(source_codes, generate_dir)


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
    transformation_rules, insert_rules = prepare_codio_rules(config)
    toc = get_toc(Path(config['workspace']['directory']), Path(config['workspace']['tex']))
    toc, tokens = codio_transformations(toc, transformation_rules, insert_rules)
    refs = make_refs(toc, chapter_counter_from=get_ref_chapter_counter_from(config))
    refs = override_refs(refs, config)
    book, metadata = make_metadata_items(config)

    chapter = None
    children_containers = [book["children"]]
    chapter_num = 0
    figure_num = 0
    exercise_num = 0
    pdfs_for_convert = []
    source_codes = []
    logging.debug("convert selected pages")

    for item in toc:
        if item.section_type == CHAPTER:
            chapter_num += 1
            figure_num = 0
            exercise_num = 0
            slug_name = slugify(item.section_name)
            chapter = item.section_name
        else:
            slug_name = slugify(item.section_name, chapter=chapter)

        logging.debug("convert page %s" % slug_name)

        converted_md = item.markdown

        if not converted_md:
            lines = cleanup_latex(item.lines)

            md_converter = LaTeX2Markdown(
                '\n'.join(lines), refs=refs, chapter_num=chapter_num, figure_num=figure_num, exercise_num=exercise_num
            )

            converted_md = md_converter.to_markdown()
            figure_num += md_converter.get_figure_counter()
            exercise_num += md_converter.get_exercise_counter()

            if md_converter.get_pdfs_for_convert():
                pdfs_for_convert += md_converter.get_pdfs_for_convert()

            if md_converter.get_source_codes():
                source_codes += md_converter.get_source_codes()

            if slug_name in tokens:
                for key, value in tokens.get(slug_name).items():
                    converted_md = converted_md.replace(key, value)

        md_path = content_dir.joinpath(slug_name + ".md")
        section, book_item = make_section_items(item, slug_name, md_path, transformation_rules)

        if item.section_type == CHAPTER or item.codio_section == "start":
            book_item["children"] = []
            if item.section_type == CHAPTER:
                children_containers = [children_containers[0]]
        elif item.codio_section == "end" and len(children_containers) > 1:
            children_containers.pop()

        children_containers[len(children_containers) - 1].append(book_item)

        if item.section_type == CHAPTER or item.codio_section == "start":
            children_containers.append(book_item["children"])

        metadata["sections"].append(section)

        write_file(md_path, converted_md)

    write_metadata(guides_dir, metadata, book)
    process_assets(config, generate_dir, pdfs_for_convert, source_codes)
