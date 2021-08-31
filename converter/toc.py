import pathlib
import yaml
import re

from pathlib import Path

from converter.guides.item import SectionItem, SECTION, CHAPTER
from converter.guides.tools import write_file, get_text_in_brackets, read_file_lines
from converter.loader import load_json_file

LATEX = 'latex'
BOOKDOWN = 'bookdown'
RST = 'rst'

TOCTREE = '.rst'
JSON = '.json'


def is_section(line):
    return line.startswith('\\section')


def is_chapter(line):
    return line.startswith('\\chapter')


def is_toc(line):
    return is_section(line) or is_chapter(line)


def is_input(line):
    line = line.lstrip()
    return line.startswith('\\input')


def is_include(line):
    line = line.lstrip()
    return line.startswith('\\include')


def input_file(line):
    return get_text_in_brackets(line)


def include_file(line):
    return get_text_in_brackets(line)


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
        res = name[0:l_pos] + name[cut_pos:r_pos] + name[r_pos + 1:]
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


def is_section_file(line):
    return line.strip().startswith("\\sectionfile")


def get_section_lines(line, tex_folder):
    section_line_re = re.compile(r"""\\sectionfile{(?P<block_name>.*?)}{(?P<block_path>.*?)}""")
    result = section_line_re.search(line)
    if result:
        file = result.group("block_path")
        if '.tex' not in file:
            file = '_{}.tex'.format(file)
        tex_file = tex_folder.joinpath(file)
        if tex_file.exists():
            with open(tex_file, 'r', errors='replace') as file:
                return file.readlines()

    return []


def process_toc_lines(lines, tex_folder, parent_folder):
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
            if is_section_file(line):
                section_lines = get_section_lines(line, parent_folder)
                for sub_line in section_lines:
                    item_lines.append(sub_line.rstrip('\n'))
        elif is_input(line) or is_include(line):
            if is_input(line):
                sub_toc = get_latex_toc(tex_folder, input_file(line))
            else:
                sub_toc = get_latex_toc(tex_folder, include_file(line))
            if sub_toc:
                toc = toc + sub_toc
            else:
                r_file = input_file(line) if is_input(line) else include_file(line)
                sub_content = get_include_lines(tex_folder, r_file)
                if sub_content:
                    item_lines.extend(sub_content)
                    line_pos += len(sub_content)
                    continue

        line_pos += 1
        if toc:
            item_lines.append(line)
    if toc and item_lines and not toc[len(toc) - 1].lines:
        toc[len(toc) - 1].lines = item_lines
    return toc


def get_include_lines(tex_folder, tex_name):
    a_path = tex_folder.joinpath(tex_name).resolve()
    if not str(a_path).endswith(".tex"):
        a_path = tex_folder.joinpath("{}.tex".format(tex_name)).resolve()
    if not a_path.exists():
        return None
    with open(a_path, 'r', errors='replace') as file:
        return file.readlines()


def get_latex_toc(tex_folder):
    lines = get_include_lines(tex_folder, tex_folder.name)
    if not lines:
        return None
    a_path = tex_folder.joinpath(tex_folder.name).resolve()
    return process_toc_lines(lines, tex_folder, a_path.parent)


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
    with open(a_path, 'r', errors='replace') as file:
        lines = file.readlines()
        return process_bookdown_lines(lines, name_without_ext)


def get_bookdown_toc(folder):
    a_path = folder.joinpath(folder.name).resolve()
    with open(a_path, 'r', errors='replace') as stream:
        content = yaml.load(stream, Loader=yaml.FullLoader)
        rmd_files = content.get('rmd_files')
        toc = []
        for file in rmd_files:
            name_without_ext = Path(file).stem
            toc += process_bookdown_file(folder.joinpath('_book'), "{}.md".format(name_without_ext), name_without_ext)
        return toc


def get_rst_toc(source_path, config_path, exercises={}):
    toc = []
    if config_path.suffix == JSON:
        json_config = load_json_file(config_path)
        chapters = json_config.get('chapters')
        for chapter in chapters:
            pages = chapters.get(chapter)
            toc.append(SectionItem(
                section_name=chapter,
                section_type='chapter',
                line_pos=0)
            )
            for page in pages:
                rst_file_name = f'{page}.rst'
                rst_file_path = pathlib.Path(source_path.joinpath(rst_file_name).resolve())
                if not rst_file_path.exists():
                    print("File %s doesn't exist\n" % rst_file_name)
                    continue
                lines = get_rst_lines(rst_file_path)
                toc += process_rst_lines(lines, exercises)
        return toc

    if config_path.suffix == TOCTREE:
        chapters = get_toctree_item(config_path, {})
        process_toctree(source_path, chapters)

        for chapter in chapters:
            pages = chapters.get(chapter)
            file_path = pathlib.Path(source_path.joinpath(chapter).resolve())
            if not file_path.exists():
                print("File %s doesn't exist\n" % chapter)
                continue
            add_toc_item(toc, file_path, 'chapter', codio_section=None)

            curr_dir = source_path.joinpath(chapter).parent
            for page in pages:
                codio_section = None
                children_pages = pages[page]
                if children_pages:
                    codio_section = 'start'

                file_path = pathlib.Path(curr_dir.joinpath(page).resolve())
                if not file_path.exists():
                    print("File %s doesn't exist\n" % page)
                    continue
                add_toc_item(toc, file_path, 'section', codio_section)

                if children_pages:
                    codio_section = None
                    for ind, child in enumerate(children_pages):
                        last_child = ind + 1 == len(children_pages)
                        if last_child:
                            codio_section = 'end'
                        file_path = pathlib.Path(curr_dir.joinpath(child).resolve())
                        if not file_path.exists():
                            print("File %s doesn't exist\n" % child)
                            continue
                        add_toc_item(toc, file_path, 'section', codio_section)
        return toc


def add_toc_item(toc, file_path, section_type, codio_section):
    name = get_chapter_name(file_path)
    lines = [line.rstrip('\r\n') for line in get_rst_lines(file_path)]

    active_code_toc_list = []
    for line in lines:
        if '.. activecode::' in line:
            if re.search(r'Ex\d+n?a', line):
                continue
            activecode_match = re.search(r'\.\. activecode:: (?P<name>.*?)$', line, flags=re.MULTILINE)
            if activecode_match:
                ex_name = activecode_match.group('name')
                ex_name = ex_name.strip().replace('-', '_')
                section_name = f'Active code: {ex_name}'
                active_code_toc_list.append(SectionItem(
                    section_name=section_name,
                    section_type=section_type,
                    line_pos=0)
                )
                content = f'{{Check It!|assessment}}(test-{ex_name.lower()})'
                active_code_toc_list[len(active_code_toc_list) - 1].lines.append(content)
            codio_section = 'start'

    toc.append(SectionItem(
        section_name=name,
        section_type=section_type,
        lines=lines,
        codio_section=codio_section,
        line_pos=0)
    )

    if active_code_toc_list:
        active_code_toc_list[len(active_code_toc_list) - 1].codio_section = 'end'
        toc.extend(active_code_toc_list)


def get_chapter_name(file_path):
    name = ''
    lines = get_rst_lines(file_path)
    for ind, line in enumerate(lines):
        next_line = lines[ind + 1] if ind + 1 < len(lines) else ''
        if name == '' and line.strip() != '' and (next_line.startswith(':::')
                                                  or next_line.startswith('===') or next_line.startswith('---')):
            name = line.strip()
            break
    return name


def process_toctree(source_path, toc_tree):
    for item in toc_tree:
        path = source_path.joinpath(item)
        var = toc_tree[item]
        res = get_toctree_item(path, var)
        if res is None:
            continue
        process_toctree(path.parent, res)


def get_toctree_item(path, structure):
    settings = []
    tocTreeFlag = False
    chaptersFlag = False
    if not Path.exists(path):
        print('File path not exist:', path)
        return

    try:
        lines = read_file_lines(path)
    except BaseException as e:
        raise BaseException(e)

    for ind, line in enumerate(lines):
        next_line = lines[ind + 1] if ind + 1 < len(lines) else ''

        if '.. toctree:' in line:
            tocTreeFlag = True
            continue
        if tocTreeFlag and line.strip().startswith(':'):
            settings.append(line.strip())
            if not next_line.strip():
                chaptersFlag = True
            continue
        if chaptersFlag:
            line = line.strip()
            if not line:
                continue

            structure[line] = {}
            if not next_line.strip() or next_line.startswith('.. '):
                break
    if not structure:
        return
    return structure


def _math(matchobj):
    content = matchobj.group('content')
    content = content.replace("\\", "")
    return f'{content}'


def get_rst_lines(path):
    with open(path, 'r', errors='replace') as file:
        return file.readlines()


def process_rst_lines(lines, exercises):
    toc = []
    item_lines = []
    contains_exercises = False
    for ind, line in enumerate(lines):
        line = line.rstrip('\r\n')
        next_line = lines[ind + 1] if ind + 1 < len(lines) else ''
        next_line = next_line.strip()
        is_chapter = next_line == "=" * len(line)
        if next_line.startswith("===") and is_chapter:
            section_name = line.replace("\\", "\\\\")
            section_name = re.compile(r""":math:`(?P<content>.*?)`""").sub(_math, section_name)
            toc.append(SectionItem(
                section_name=section_name,
                section_type="section",
                line_pos=0)
            )
            item_lines = []
        if line.startswith(".. extrtoolembed::"):
            result = re.match(r'\.\. extrtoolembed:: \'(?P<name>.*?)\'', line)
            if result:
                contains_exercises = True
                ex_name = result.group('name')
                section_name = f'Exercise: {ex_name}'
                exercise = exercises.get(ex_name.lower(), {})
                exercise_path = exercise.get('ex_path', '')
                toc.append(SectionItem(
                    section_name=section_name,
                    section_type="section",
                    exercise=True,
                    exercise_path=exercise_path,
                    line_pos=0)
                )
                content = f'{{Check It!|assessment}}(test-{ex_name.lower()})'
                toc[len(toc) - 1].lines.append(content)
        item_lines.append(line)
    if toc and item_lines and not toc[0].lines:
        item_lines.append('')
        toc[0].lines = item_lines
        toc[0].contains_exercises = contains_exercises
    return toc


def print_to_yaml(structure, workspace_path, source_path, config_path, data_format):
    yaml_structure = f"""workspace:
  directory: {workspace_path}
  sources: {source_path}
  {data_format}: {config_path}
assets:
sections:
"""
    first_item = True
    exercises_flag = False
    for ind, item in enumerate(structure):
        yaml_structure += f"  - name: \"{item.section_name}\"\n    type: {item.section_type}\n"
        if item.codio_section:
            yaml_structure += f"    codio_section: \"{item.codio_section}\"\n"

        next_item = structure[ind + 1] if ind + 1 < len(structure) else {}
        prev_item = structure[ind - 1]

        if exercises_flag and not prev_item.exercise:
            yaml_structure += "    configuration:\n" \
                              "      layout: 2-panels\n"
        elif prev_item.exercise and not item.exercise:
            yaml_structure += "    configuration:\n" \
                              "      layout: 1-panel\n"

        if item.contains_exercises:
            yaml_structure += "    codio_section: start\n"
            exercises_flag = True
        elif exercises_flag and not next_item.exercise:
            yaml_structure += "    codio_section: end\n"
            exercises_flag = False

        if first_item:
            first_item = False
            yaml_structure += "    configuration:\n      layout: 1-panel\n"
    return yaml_structure


def generate_toc(output_path, source_path, config_path, content_type, ignore_exists=True):
    workspace_dir = Path(source_path).parts[0]
    workspace_path = Path.cwd().parent.joinpath(workspace_dir).resolve()
    source_path = Path.cwd().parent.joinpath(source_path).resolve()
    config_path = Path.cwd().parent.joinpath(config_path).resolve()
    output_path = Path(output_path)

    if output_path.exists() and not ignore_exists:
        raise Exception("Output dir already exists")
    output_path.mkdir(parents=True, exist_ok=ignore_exists)

    if content_type == LATEX:
        toc = get_latex_toc(config_path)
    elif content_type == BOOKDOWN:
        toc = get_bookdown_toc(config_path)
    elif content_type == RST:
        toc = get_rst_toc(source_path, config_path)
    else:
        raise Exception("Unknown source type")

    if toc is None:
        raise Exception("TOC is empty")

    content = print_to_yaml(toc, workspace_path, source_path, config_path, content_type)
    a_path = output_path.joinpath("codio_structure.yml").resolve()
    write_file(a_path, content)
