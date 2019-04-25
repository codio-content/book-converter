import yaml

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


def cleanup_name(name):
    l_pos = name.find('{')
    r_pos = name.find('}')
    cut_pos = l_pos + 1
    if l_pos != -1 and r_pos != -1 and l_pos < r_pos:
        if name[l_pos + 1] == '\\':
            cut_pos = name.find(' ', l_pos)
        else:
            for pos in range(l_pos, -1, -1):
                if name[pos] == '\\':
                    l_pos = pos + 1
                    break
        if l_pos != 0:
            l_pos = l_pos - 1
        else:
            cut_pos += 1
        res = name[0:l_pos] + name[cut_pos:r_pos] + name[r_pos+1:]
        return cleanup_name(res)
    return name


def get_name(line):
    level = 0
    start = 0
    end = len(line)
    for pos, ch in enumerate(line):
        if ch == '{':
            if start == 0:
                start = pos
            else:
                level += 1
        elif ch == '}':
            if level == 0:
                end = pos
                break
            else:
                level -= 1
    return cleanup_name(line[start + 1:end])


def get_bookdown_name(line):
    name = line[line.index(' ') + 1:].strip()
    if '{' in name and name.endswith('}'):
        name = name[0:name.rfind('{') - 1]
        name = name.strip()
    return name


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
            sub_toc = get_latex_toc(tex_folder, input_file(line))
            if sub_toc:
                toc = toc + sub_toc
        line_pos += 1
        if toc:
            item_lines.append(line)
    if toc and item_lines and not toc[len(toc) - 1].lines:
        toc[len(toc) - 1].lines = item_lines
    return toc


def get_latex_toc(tex_folder, tex_name):
    a_path = tex_folder.joinpath(tex_name).resolve()
    with open(a_path) as file:
        lines = file.readlines()
        return process_toc_lines(lines, tex_folder)


def process_bookdown_lines(lines, name_without_ext):
    toc = []
    item_lines = []
    line_pos = 1
    quotes = False
    for line in lines:
        line = line.rstrip('\r\n')
        if '\\begin' in line:
            line = line.strip()
        if '```' in line:
            line = line.strip()
            quotes = not quotes
        top_level = not quotes and (line.startswith('# ') or line.startswith('## '))
        if top_level:
            if toc:
                if item_lines:
                    toc[len(toc) - 1].lines = item_lines
                item_lines = []
            section_type = CHAPTER if line.startswith('# ') else SECTION
            toc.append(SectionItem(
                section_name="{}----{}".format(name_without_ext, get_bookdown_name(line)),
                section_type=section_type,
                line_pos=line_pos)
            )
        if toc:
            item_lines.append(line)
        line_pos += 1
    if toc and item_lines and not toc[len(toc) - 1].lines:
        toc[len(toc) - 1].lines = item_lines
    return toc


def process_bookdown_file(folder, name, name_without_ext):
    a_path = folder.joinpath(name).resolve()
    with open(a_path) as file:
        lines = file.readlines()
        return process_bookdown_lines(lines, name_without_ext)


def get_bookdown_toc(folder, name):
    a_path = folder.joinpath(name).resolve()
    with open(a_path, 'r') as stream:
        content = yaml.load(stream)
        rmd_files = content.get('rmd_files')
        toc = []
        for file in rmd_files:
            name_without_ext = Path(file).stem
            toc += process_bookdown_file(folder.joinpath('_book'), "{}.md".format(name_without_ext), name_without_ext)
        return toc


def print_to_yaml(structure, tex, bookdown=False):
    file_format = "bookdown: {}".format(tex.name) if bookdown else "tex: {}".format(tex.name)
    yaml_structure = """workspace:
  directory: {}
  {}
assets:
  - code
sections:
""".format(tex.parent.resolve(), file_format)
    first_item = True
    for item in structure:
        yaml_structure += "  - name: \"{}\"\n    type: {}\n".format(item.section_name, item.section_type)
        if first_item:
            first_item = False
            yaml_structure += "    configuration:\n      layout: 2-panels\n"
    return yaml_structure


def generate_toc(file_path, structure_path, ignore_exists=False):
    path = Path(file_path)
    if path.exists() and not ignore_exists:
        raise Exception("Path exists")
    tex = Path(structure_path)
    bookdown = str(structure_path).endswith('_bookdown.yml')
    if bookdown:
        toc = get_bookdown_toc(tex.parent, tex.name)
    else:
        toc = get_latex_toc(tex.parent, tex.name)
    path.mkdir(parents=True, exist_ok=ignore_exists)

    content = print_to_yaml(toc, tex, bookdown=bookdown)
    a_path = path.joinpath("codio_structure.yml").resolve()
    write_file(a_path, content)
