from pathlib import Path

from converter.guides.item import SectionItem, SECTION, CHAPTER
from converter.guides.tools import write_file, get_text_in_brackets


def is_section(line):
    return line.startswith('\\section')


def is_chapter(line):
    return line.startswith('\\chapter')


def is_toc(line):
    return is_section(line) or is_chapter(line)


def is_input(line):
    return line.startswith('\\input')


def input_file(line):
    return line[7:-1]


def get_name(line):
    return get_text_in_brackets(line)


def process_toc_lines(lines, tex_folder):
    toc = []
    line_pos = 1
    item_lines = []
    for line in lines:
        line = line.rstrip('\r\n')
        if is_toc(line):
            if toc:
                if item_lines:
                    toc[len(toc) - 1].lines = item_lines
                item_lines = []
            section_type = CHAPTER if is_chapter(line) else SECTION
            toc.append(SectionItem(section_name=get_name(line), section_type=section_type, line_pos=line_pos))
        elif is_input(line):
            sub_toc = get_toc(tex_folder, input_file(line))
            if sub_toc:
                toc = toc + sub_toc
        line_pos += 1
        if toc:
            item_lines.append(line)
    if toc and item_lines and not toc[len(toc) - 1].lines:
        toc[len(toc) - 1].lines = item_lines
    return toc


def get_toc(tex_folder, tex_name):
    a_path = tex_folder.joinpath(tex_name).resolve()
    with open(a_path) as file:
        lines = file.readlines()
        return process_toc_lines(lines, tex_folder)


def print_to_yaml(structure, tex):
    yaml_structure = """workspace:
  directory: {}
  tex: {}
assets:
  - code
sections:
""".format(tex.parent.resolve(), tex.name)
    first_item = True
    for item in structure:
        yaml_structure += "  - name: {}\n    type: {}\n".format(item.section_name, item.section_type)
        if first_item:
            first_item = False
            yaml_structure += "    configuration:\n      layout: 2-panels\n"
    return yaml_structure


def generate_toc(file_path, tex_path, ignore_exists=False):
    path = Path(file_path)
    if path.exists() and not ignore_exists:
        raise Exception("Path exists")
    tex = Path(tex_path)
    toc = get_toc(tex.parent, tex.name)
    path.mkdir(parents=True, exist_ok=ignore_exists)

    content = print_to_yaml(toc, tex)
    a_path = path.joinpath("codio_structure.yml").resolve()
    write_file(a_path, content)
