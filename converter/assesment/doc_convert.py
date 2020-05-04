import re
import shutil
import uuid

import yaml
import logging
from pathlib import Path

from converter.guides.tools import write_file, slugify, write_json
from converter.guides.item import SectionItem, CHAPTER
from converter.refs import get_ref_chapter_counter_from


def generate_assesment_toc(source_path, structure_path, ignore_exists=False):
    path = Path(source_path)
    if path.exists() and not ignore_exists:
        raise Exception("Path exists")
    structure = Path(structure_path)
    path.mkdir(parents=True, exist_ok=ignore_exists)
    toc = get_assesment_toc(structure.parent, structure.name)
    content = to_yaml(toc, structure)
    a_path = path.joinpath("codio_structure.yml").resolve()
    write_file(a_path, content)


def get_assesment_toc(tex_folder, tex_name):
    lines = get_assesment_lines(tex_folder, tex_name)
    if not lines:
        return None
    return process_assesment_lines(lines)


def get_assesment_lines(folder, name):
    a_path = folder.joinpath(name).resolve()
    with open(a_path, 'r', errors='replace') as file:
        return file.readlines()


def process_assesment_lines(lines):
    toc = []
    item_lines = []
    header = False
    for line in lines:
        line = line.rstrip('\r\n')

        if match_alt_header(line):
            section_name = item_lines[len(item_lines) - 1]
            item_lines.pop()
            item_lines.append(line)
            item_lines = []
            header = True
            continue

        if match_part_header(line):
            item_lines = []
            section_name = match_part_header(line).string.strip('**')
            header = True

        if match_header(line):
            item_lines = []
            section_name = match_header(line).string.strip('#').strip()
            header = True

        if header:
            toc.append(SectionItem(
                section_name=section_name,
                section_type='section',
                line_pos=0)
            )
            toc[len(toc) - 1].lines = item_lines
            header = False

        item_lines.append(line)

    return toc


def match_header(line):
    return re.search(r""" {0,3}#{1,6}(?:\n|\s+?(.*?))""", line)


def match_alt_header(line):
    return re.search(r""" {0,3}(?:=|-)+ *$""", line)


def match_part_header(line):
    return re.search(r"""^\*\*Part \d+:.*?\*\*""", line)


def to_yaml(structure, source_path):
    source = "source: {}".format(source_path.name)
    yaml_structure = """workspace:
  directory: {}
  {}
sections:
""".format(source_path.parent.resolve(), source)
    for item in structure:
        yaml_structure += "  - name: \"{}\"\n    type: {}\n".format(item.section_name, item.section_type)
    return yaml_structure


def load_assesment_docs_config(target_path):
    global config_path
    target_path = Path(target_path)
    config_path = target_path
    if target_path.is_dir():
        config_path = target_path.joinpath("content_structure.yml")
        if not config_path.is_file():
            config_path = target_path.joinpath("content_structure.yaml")
        if not config_path.is_file():
            raise BaseException("Structure not found")
    with open(config_path, 'r') as stream:
        try:
            return yaml.load(stream), config_path.parent
        except yaml.YAMLError as exc:
            logging.error("load config file exception", exc)
            raise BaseException("load config file exception")


def convert_assesment_doc(config, base_path, yes=False):
    base_dir = base_path
    generate_dir = base_dir.joinpath("generate")
    if not prepare_base_directory(generate_dir, yes):
        return
    logging.debug("start converting %s" % generate_dir)
    guides_dir, content_dir = prepare_structure(generate_dir)
    transformation_rules, insert_rules = prepare_codio_rules(config)
    toc = get_assesment_toc(Path(config['workspace']['directory']), Path(config['workspace']['source']))
    toc, tokens = codio_transformations(toc, transformation_rules, insert_rules)
    book, metadata = make_metadata_items(config)

    chapter = None
    children_containers = [book["children"]]
    chapter_num = get_ref_chapter_counter_from(config) - 1
    logging.debug("convert selected pages")

    for item in toc:
        if item.section_type == CHAPTER:
            chapter_num += 1
            slug_name = slugify(item.section_name)
            chapter = item.section_name
        else:
            slug_name = slugify(item.section_name, chapter=chapter)

        logging.debug("convert page {} - {}".format(slug_name, chapter_num))

        out_md = '\n'.join(item.lines)

        md_path = content_dir.joinpath(slug_name + ".md")
        section, book_item = make_section_items(item, slug_name, md_path, transformation_rules, out_md)

        if item.section_type == CHAPTER or item.codio_section == "start":
            book_item["children"] = []
            if item.section_type == CHAPTER:
                children_containers = [children_containers[0]]
        elif item.codio_section == "end" and len(children_containers) > 1:
            children_containers.pop()

        children_containers[len(children_containers) - 1].append(book_item)

        if item.section_type == CHAPTER or item.codio_section == "start":
            children_containers.append(book_item["children"])
        if section:
            metadata["sections"].append(section)

        write_file(md_path, out_md)

    write_metadata(guides_dir, metadata, book)


def prepare_base_directory(generate_dir, yes=False):
    if generate_dir.exists():
        if not yes:
            name = input("destination directory exists, continue? Y/n: ")
            if name.lower().strip() == 'n':
                return False
        shutil.rmtree(generate_dir, ignore_errors=True)
    return True


def write_metadata(guides_dir, metadata, book):
    logging.debug("write metadata")
    metadata_path = guides_dir.joinpath("metadata.json")
    book_path = guides_dir.joinpath("book.json")
    write_json(metadata_path, metadata)
    write_json(book_path, book)


def fix_title(name):
    if '----' in name:
        return name[name.find('----') + 4:]
    return name


def make_section_items(item, slug_name, md_path, transformation_rules, converted_md):
    book_item = {
        "id": slug_name,
        "title": fix_title(item.section_name),
        "type": get_section_type(item),
        "pageId": slug_name
    }
    section = {
        "id": slug_name,
        "title": fix_title(item.section_name),
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
    if not converted_md:
        del book_item["pageId"]
        section = None
    return section, book_item


def get_section_type(item):
    if item.codio_section == "start":
        return "section"
    return "chapter" if item.section_type == CHAPTER else "page"


def get_guide_content_path(file_path):
    file_path = str(file_path)
    pos = file_path.find(".guides")
    if pos == -1:
        return file_path
    return file_path[pos:]


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


def modify_rules_position(rules, start_position, delta):
    for rule in rules:
        position = rule.get('position')
        if position < start_position:
            continue
        rule['position'] = rule['position'] + delta


def make_relative(i, item):
    copied = i.copy()
    copied["position"] = int(copied.get("position")) - item.line_pos
    return copied


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


def prepare_structure(generate_dir):
    generate_dir.mkdir()
    guides_dir = generate_dir.joinpath(".guides")
    guides_dir.mkdir()
    content_dir = guides_dir.joinpath("content")
    content_dir.mkdir()

    return guides_dir, content_dir
