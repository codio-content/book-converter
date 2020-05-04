import re
import yaml
import logging
from pathlib import Path

from converter.convert import prepare_base_directory, prepare_structure, prepare_codio_rules, \
    codio_transformations, make_metadata_items, make_section_items, write_metadata
from converter.guides.tools import write_file, slugify
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
