import logging
import pathlib
import re
import shutil
import uuid
import yaml

from collections import OrderedDict
from pathlib import Path

from converter.opendsa_assessments.code_workout import create_assessments_data
from converter.rst.assessments.active_code.write_data import create_active_code_files
from converter.rst.assessments.assessment_const import MULTIPLE_CHOICE, FILL_IN_THE_BLANKS, FREE_TEXT, PARSONS, \
    ACTIVE_CODE
from converter.rst2markdown import Rst2Markdown, OPEN_DSA_CDN
from converter.toc import get_latex_toc, get_bookdown_toc, get_rst_toc
from converter.guides.tools import slugify, write_file, write_json, parse_csv_lines
from converter.guides.item import SectionItem, CHAPTER
from converter.latex2markdown import LaTeX2Markdown
from converter.bookdown2markdown import BookDown2Markdown
from converter.assets import copy_assets, convert_assets, process_source_code, copy_files_from_bookdown_folder
from converter.refs import make_refs, override_refs, get_ref_chapter_counter_from, make_bookdown_refs
from converter.optimizer import optimize

RST_TOCTREE = 'rst'
RST_JSON = 'json'


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
        '\\vspace', '\\newpage', '\\noindent',
        '\\ttfamily', '\\chapter', '\\section', '\\newcommand', '\\vfill', '\\pagebreak'
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


def prepare_structure(chapter_dir):
    chapter_dir.mkdir(parents=True)
    guides_dir = chapter_dir.joinpath(".guides")
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
    # if not converted_md:
    #     del book_item["pageId"]
    #     section = None
    return section, book_item


def make_odsa_ex_files(path):
    path = path.replace("\\", "/")
    return {
               "path": "#tabs",
               "action": "close"
           }, {
               "path": f"exercises/{path}/starter_code.java",
               "panel": 0,
               "action": "open"
           }


def process_assets(config, generate_dir, pdfs_for_convert, source_codes, bookdown=False):
    logging.debug("copy assets")
    copy_assets(config, generate_dir)

    if bookdown:
        copy_files_from_bookdown_folder(config, generate_dir)

    if pdfs_for_convert:
        logging.debug("convert included pdfs")
        convert_assets(config, generate_dir, pdfs_for_convert, bookdown=bookdown)

    if source_codes:
        logging.debug("process source codes")
        use_code_folder = bool(config.get('workspace', {}).get('useCodeFolder', True))
        process_source_code(source_codes, generate_dir, use_code_folder)

    optimization_config = config.get('optimization', {})
    if optimization_config:
        optimize(optimization_config, generate_dir)


def write_metadata(guides_dir, metadata, book):
    logging.debug("write metadata")

    metadata_path = guides_dir.joinpath("metadata.json")
    book_path = guides_dir.joinpath("book.json")
    write_json(metadata_path, metadata)
    write_json(book_path, book)


def convert_assessment(assessment):
    if assessment.type == 'custom':
        return convert_custom_assessment(assessment)
    elif assessment.type == 'test':
        return convert_code_workout_assessment(assessment)
    elif assessment.type == MULTIPLE_CHOICE:
        return convert_mc_assessment(assessment)
    elif assessment.type == FILL_IN_THE_BLANKS:
        return convert_fillintheblanks_assessment(assessment)
    elif assessment.type == FREE_TEXT:
        return convert_freetext_assessment(assessment)
    elif assessment.type == PARSONS:
        return convert_parsons_assessment(assessment)
    elif assessment.type == ACTIVE_CODE:
        return convert_activecode_assessment(assessment)


def convert_custom_assessment(assessment):
    return {
        'type': 'custom',
        'taskId': assessment.id,
        'source': {
            'name': assessment.name,
            'arePartialPointsAllowed': False,
            'oneTimeTest': False,
            'points': assessment.points,
            'instructions': assessment.options.get('question', '')
        }
    }


def convert_code_workout_assessment(assessment):
    class_name = assessment.options.get('class_name', '')
    method_name = assessment.options.get('method_name', '')
    instructions = assessment.options.get('question', '')
    instructions = re.sub(r'<img src=\"https?://.*?(Exercises.*?)\">',
                          fr'<img src="{OPEN_DSA_CDN}/\1">', instructions)
    ex_path = assessment.options.get('ex_path', '')
    tests = assessment.options.get('tests', '')
    test_matches = parse_csv_lines(tests)
    instructions = instructions_with_examples(test_matches, instructions, method_name)

    return {
        'type': 'test',
        'taskId': assessment.id,
        'source': {
            'name': assessment.name,
            'instructions': instructions,
            'command': f'.guides/secure/assessments/run.py {class_name} {ex_path}',
            'arePartialPointsAllowed': True,
            'oneTimeTest': False,
            'points': assessment.points
        }
    }


def convert_activecode_assessment(assessment):
    options = assessment.options
    instructions = options.get('text', '')
    class_name = options.get('class_name', '')

    return {
        "type": "test",
        "taskId": assessment.id,
        "source": {
            "name": f'Active code ({assessment.name})',
            "showName": True,
            "instructions": instructions,
            "command": f'.guides/secure/active_code/run.py {class_name} {assessment.name}',
            "timeoutSeconds": 300,
            "guidance": "",
            "showGuidanceAfterResponseOption": {
                "type": "Always"
            },
            "points": assessment.points,
            "oneTimeTest": False,
            "arePartialPointsAllowed": True,
            "metadata": {
                "tags": [
                    {
                        "name": "Assessment Type",
                        "value": "Advanced Code Test"
                    }
                ],
                "files": [
                    f".guides/test1/{class_name}.java"
                ],
                "opened": [
                    {
                        "type": "file",
                        "panelNumber": 0,
                        "content": f".guides/{assessment.name}/{class_name}.java"
                    }
                ]
            },
            "bloomsObjectiveLevel": "",
            "learningObjectives": ""
        }
    }


def convert_mc_assessment(assessment):
    answers_list = []
    options = assessment.options
    question = options.get('question', '')
    answers = options.get('answers', [])
    feedback_list = options.get('feedback', [])
    isRandomized = options.get('random', False)
    multipleResponse = options.get('multipleResponse', False)
    exercise_type = options.get('type', None)
    feedback_final = []
    answer_count = 1

    if exercise_type == 'clickablearea':
        feedback_final.append(options.get('feedback', ''))
        answers = options.get('answers', [])
        for item in answers:
            answer_count += 1
            answer_id = f'{assessment.name}-answer-{answer_count}'
            answer = {
                "_id": answer_id,
                "correct": item['is_correct'],
                "answer": item['answer']
            }
            answers_list.append(answer)

    elif exercise_type == 'mchoice':
        correct_answer = [a.strip() for a in options.get('correct', '').split(',')]
        for answer in answers:
            answer_count += 1
            items = list(answer.items())
            answer_name = str(items[0][0])
            answer_name = answer_name.replace('answer_', '')
            answer_text = f'<b>{answer_name.upper()}.</b> {items[0][1]}'
            is_correct = answer_name.lower() in correct_answer
            answer_id = f'{assessment.name}-answer-{answer_count}'
            answer = {
                "_id": answer_id,
                "correct": is_correct,
                "answer": answer_text
            }
            answers_list.append(answer)

        for ind, feedback in enumerate(feedback_list, start=1):
            if type(feedback) != str:
                items = list(feedback.items())
                feedback_name = items[0][0].replace('feedback_', '')
                value = f'<b>{feedback_name.upper()}</b>: {items[0][1]}'
                feedback_final.append(value)
            else:
                value = f'<b>{ind}.</b> {feedback}'
                feedback_final.append(value)

    return {
        "type": assessment.type,
        "taskId": assessment.id,
        "source": {
            "name": f'Multiple Choice ({assessment.name})',
            "showName": True,
            "instructions": question,
            "multipleResponse": multipleResponse,
            "isRandomized": False,
            "answers": answers_list,
            "guidance": '\n\n'.join(feedback_final),
            "showGuidanceAfterResponseOption": {
                "type": "Always"
            },
            "showExpectedAnswer": True,
            "points": assessment.points,
            "incorrectPoints": 0,
            "arePartialPointsAllowed": False,
            "bloomsObjectiveLevel": "",
            "learningObjectives": ""
        }
    }


def convert_fillintheblanks_assessment(assessment):
    options = assessment.options
    text = options.get('text', {})
    text = text.replace('|blank|', '[blank]')

    token_blank = []
    token_text = []
    split_text = text.split('[blank]')
    if len(split_text) == 1:
        token_text.append(f'{split_text[0]}\n')
        token_text.append(0)
    else:
        for ind, item in enumerate(split_text):
            token_text.append(item)
            if ind != len(split_text) - 1:
                token_text.append(0)

    for opt in options.keys():
        if opt == 'correct_answers':
            blank_match = re.search(r'\[blank]', text)
            if blank_match:
                for item in options[opt]:
                    item = item.replace('$', '\\$')
                    text = text.replace('[blank]', f'<<<{item}>>>', 1)
                    token_blank.append(item)
            else:
                correct_answer = list(options[opt].keys())[0]
                correct_answer = re.sub(r'\\', '\\\\', correct_answer)
                text = f'{text}\n<<<{correct_answer}>>>'
                token_blank.append(correct_answer)

    tokens = {
        "blank": token_blank,
        "text": token_text,
        "regexPositions": []
    }

    return {
        "type": assessment.type,
        "taskId": assessment.id,
        "source": {
            "name": f'Fill in the Blank ({assessment.name})',
            "showName": True,
            "instructions": "",
            "showValues": False,
            "text": text,
            "distractors": "",
            "guidance": "",
            "showGuidanceAfterResponseOption": {
                "type": "Always"
            },
            "showExpectedAnswer": True,
            "points": assessment.points,
            "arePartialPointsAllowed": False,
            "metadata": {
                "tags": [
                    {
                        "name": "Assessment Type",
                        "value": "Fill in the Blanks"
                    }
                ],
                "files": [],
                "opened": []
            },
            "bloomsObjectiveLevel": "",
            "learningObjectives": "",
            "tokens": tokens
        }
    }


def convert_freetext_assessment(assessment):
    options = assessment.options
    question = options.get('question', {})

    instructions = f'{question}\n\n'
    for ind, item in enumerate(options, start=1):
        if item.startswith('option_'):
            instructions += f'{ind}. {options[item]}\n\n'

    return {
        "type": assessment.type,
        "taskId": assessment.id,
        "source": {
            "name": assessment.name,
            "showName": False,
            "instructions": instructions,
            "guidance": '',
            "showGuidanceAfterResponseOption": {
                "type": "Always"
            },
            "previewType": "NONE",
            "arePartialPointsAllowed": False,
            "oneTimeTest": False,
            "points": assessment.points,
            "rubrics": [],
            "metadata": {
                "tags": [
                    {
                        "name": "Assessment Type",
                        "value": "Free Text"
                    }
                ],
                "files": [],
                "opened": []
            },
            "bloomsObjectiveLevel": "",
            "learningObjectives": ""
        }
    }


def convert_parsons_assessment(assessment):
    options = assessment.options
    instructions = options.get('question', '')
    feedback = options.get('feedback', '')
    initial = options.get('initial', '')
    max_distractors = options.get('max_distractors', 0)
    trashId = 'sortableTrash' if max_distractors > 0 else ''

    return {
        "type": assessment.type,
        "taskId": assessment.id,
        "source": {
            "name": f'Parsons ({assessment.name})',
            "showName": True,
            "instructions": instructions,
            "initial": initial,
            "options": f"{{\"sortableId\":\"sortable\",\"max_wrong_lines\":{max_distractors},\"exec_limit\":2500,"
                       f"\"can_indent\":false,\"x_indent\":50,\"lang\":\"en\",\"trashId\":\"{trashId}\"}}",
            "grader": "1",
            "guidance": feedback,
            "showGuidanceAfterResponseOption": {
                "type": "Always"
            },
            "points": assessment.points,
            "oneTimeTest": False,
            "metadata": {
                "tags": [
                    {
                        "name": "Assessment Type",
                        "value": "Parsons Puzzle"
                    }
                ],
                "files": [],
                "opened": []
            },
            "bloomsObjectiveLevel": "",
            "learningObjectives": ""
        }
    }


def instructions_with_examples(test_matches, instructions, method_name):
    examples_list = []
    examples = ''
    for item in test_matches:
        example = _get_example(item, method_name)
        if example:
            examples_list.append(example)
    if examples_list:
        examples = '\n'.join(examples_list)
        examples = f'\nExamples:\n\n{examples}'
    return f'{instructions}{examples}'


def _get_example(item, method_name):
    example = None
    message = item[2] if len(item) == 3 else None
    if message and message == 'example':
        actual = item[0]
        actual = re.sub(r'new\s+[a-zA-Z0-9]+(\s*\[\s*])+\s*', '', actual)
        expected = item[1]
        example = f'`{method_name}({actual}) -> {expected}`\n\n'
    return example


def write_assessments(guides_dir, assessments):
    if not assessments:
        return
    logging.debug("write assessments")
    assessments_path = guides_dir.joinpath("assessments.json")
    unique_assessments = list({object_.id: object_ for object_ in assessments}.values())
    converted_assessments = list(map(convert_assessment, unique_assessments))
    write_json(assessments_path, converted_assessments, sort_keys=False)


def convert(config, base_path, yes=False):
    base_dir = base_path
    generate_dir = base_dir.joinpath("generate")
    if not prepare_base_directory(generate_dir, yes):
        return

    logging.debug("start converting %s" % generate_dir)
    guides_dir, content_dir = prepare_structure(generate_dir)
    transformation_rules, insert_rules = prepare_codio_rules(config)
    toc = get_latex_toc(Path(config['workspace']['directory']), Path(config['workspace']['tex']))
    toc, tokens = codio_transformations(toc, transformation_rules, insert_rules)
    refs = make_refs(toc, chapter_counter_from=get_ref_chapter_counter_from(config))
    refs = override_refs(refs, config)
    book, metadata = make_metadata_items(config)
    remove_trinket = config['workspace'].get('removeTrinket', False)
    remove_exercise = config['workspace'].get('removeExercise', False)

    detect_asset_ext = assets_extension(Path(config['workspace']['directory']))

    chapter = None
    children_containers = [book["children"]]
    chapter_num = get_ref_chapter_counter_from(config) - 1
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

        logging.debug("convert page {} - {}".format(slug_name, chapter_num))

        converted_md = item.markdown

        if not converted_md:
            lines = cleanup_latex(item.lines)

            md_converter = LaTeX2Markdown(
                lines,
                refs=refs, chapter_num=chapter_num, figure_num=figure_num,
                exercise_num=exercise_num, remove_trinket=remove_trinket,
                remove_exercise=remove_exercise, detect_asset_ext=detect_asset_ext,
                load_workspace_file=workspace_file(Path(config['workspace']['directory']))
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
        section, book_item = make_section_items(item, slug_name, md_path, transformation_rules, converted_md)

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

        write_file(md_path, converted_md)

    write_metadata(guides_dir, metadata, book)
    process_assets(config, generate_dir, pdfs_for_convert, source_codes)


def workspace_file(base_src_dir):
    def load_workspace_file(path):
        if '.' not in path:
            path = f"{path}.tex"
        file = base_src_dir.joinpath(path)
        if file.exists():
            with open(file, 'r', errors='replace') as file:
                return file.read()
        return ''

    return load_workspace_file


def assets_extension(base_src_dir):
    possible_exts = ['pdf', 'png', 'jpg']

    def detect_asset_ext(asset_path):
        for ext in possible_exts:
            file = base_src_dir.joinpath('_bookdown_files').joinpath('{}.{}'.format(asset_path, ext))
            if file.exists():
                return ext
            file = base_src_dir.joinpath('{}.{}'.format(asset_path, ext))
            if file.exists():
                return ext

    return detect_asset_ext


def cleanup_bookdown(lines):
    lines = lines[1:]
    return lines


def get_labels(lines):
    label = ''
    for line in lines:
        if line.startswith('.. _'):
            label = line.strip()[4:-1]
    return label


def convert_bookdown(config, base_path, yes=False):
    base_dir = base_path
    generate_dir = base_dir.joinpath("generate")
    if not prepare_base_directory(generate_dir, yes):
        return

    logging.debug("start converting %s" % generate_dir)
    guides_dir, content_dir = prepare_structure(generate_dir)
    transformation_rules, insert_rules = prepare_codio_rules(config)
    toc = get_bookdown_toc(Path(config['workspace']['directory']), Path(config['workspace']['bookdown']))
    toc, tokens = codio_transformations(toc, transformation_rules, insert_rules)
    book, metadata = make_metadata_items(config)

    chapter = None
    chapter_num = get_ref_chapter_counter_from(config) - 1
    figure_num = 0
    children_containers = [book["children"]]
    pdfs_for_convert = []
    logging.debug("convert selected pages")

    detect_asset_ext = assets_extension(Path(config['workspace']['directory']))
    refs = make_bookdown_refs(config)

    for item in toc:
        if item.section_type == CHAPTER:
            chapter_num += 1
            figure_num = 0
            slug_name = slugify(item.section_name)
            chapter = item.section_name
        else:
            slug_name = slugify(item.section_name, chapter=chapter)

        logging.debug("convert page {} - {}".format(slug_name, chapter_num))

        converted_md = item.markdown

        if not converted_md:
            lines = cleanup_bookdown(item.lines)
            md_converter = BookDown2Markdown(
                lines,
                chapter_num=chapter_num, figure_num=figure_num, assets_extension=detect_asset_ext, refs=refs
            )
            figure_num += md_converter.get_figure_counter()
            converted_md = md_converter.to_markdown()
            if md_converter.get_pdfs_for_convert():
                pdfs_for_convert += md_converter.get_pdfs_for_convert()

            if slug_name in tokens:
                for key, value in tokens.get(slug_name).items():
                    converted_md = converted_md.replace(key, value)

        md_path = content_dir.joinpath(slug_name + ".md")
        section, book_item = make_section_items(item, slug_name, md_path, transformation_rules, converted_md)

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

        write_file(md_path, converted_md)

    write_metadata(guides_dir, metadata, book)

    process_assets(config, generate_dir, pdfs_for_convert, [], bookdown=True)


def get_code_workout_exercises(workspace_dir):
    exercises = {}
    code_dir = workspace_dir.joinpath('ODSAprivate-master')
    code_dir = pathlib.Path(code_dir)
    if not code_dir.exists():
        return {}
    ex_dirs = [p for p in code_dir.iterdir() if not p.is_file()]
    for directory in ex_dirs:
        yaml_files = directory.glob("*.yaml")
        ex_group_dir = pathlib.Path(directory).name
        ex_group_dir = Path(ex_group_dir)
        for file in yaml_files:
            with open(file, 'r') as stream:
                try:
                    data = yaml.load(stream, Loader=yaml.FullLoader)
                    ex_path = ex_group_dir.joinpath(file.stem)
                    if isinstance(data, list):
                        data = data[0]
                    curr_ver = data.get('current_version', '')
                    prompts = curr_ver.get('prompts', '')[0]['coding_prompt']
                    name = data.get('name', '').lower()
                    exercises[name] = {
                        'name': name,
                        'ex_path': str(ex_path),
                        'file_name': file.stem,
                        'dir_name': directory.name,
                        'class_name': prompts.get('class_name', ''),
                        'method_name': prompts.get('method_name', ''),
                        'question': prompts.get('question', ''),
                        'starter_code': prompts.get('starter_code', ''),
                        'wrapper_code': prompts.get('wrapper_code', ''),
                        'tests': prompts.get('tests', '')
                    }
                except yaml.YAMLError as exc:
                    logging.error("load file exception", exc)
                    raise BaseException("load file exception")
    return exercises


def process_iframe_images(config, generate_dir, iframe_images):
    write_iframe = bool(config.get('opendsa', {}).get('writeIframe', False))
    if write_iframe and iframe_images:
        for image in iframe_images:
            write_path = generate_dir.joinpath(image.path)
            write_path.parent.mkdir(exist_ok=True, parents=True)
            write_file(write_path, image.content)


def prepare_figure_numbers(toc):
    tag_references = dict()
    chapter_num = 0
    subsection_num = 0
    for item in toc:
        if item.section_type == CHAPTER:
            subsection_num = 0
            chapter_num += 1
        else:
            subsection_num += 1

        prepare_figure_numbers_for_item(item, chapter_num, subsection_num, tag_references)
    return tag_references


def prepare_figure_numbers_for_item(item, chapter_num, subsection_num, tag_references):
    figure_counter = 1
    for i in range(len(item.lines)):
        tag = re.search(r"""(\.\.[ ]_(?P<name>[a-zA-Z0-9]*):)""", item.lines[i])
        if tag:
            tag = tag.group('name')
            tag_references[tag] = f'{chapter_num}.{subsection_num}.{figure_counter}'

        matchobj = re.search(r"""(\.\.[ ](?P<figure_type>[a-z]*)::)""", item.lines[i])
        figure_type = matchobj.group('figure_type') if matchobj and matchobj.group('figure_type') is not None else False
        if figure_type and figure_type in ['odsafig', 'figure', 'inlineav', 'topic']:
            item.lines[i] = item.lines[i].replace(
                f'{figure_type}::',
                f'{figure_type}:: :figure_number:{subsection_num}.{figure_counter}:')
            figure_counter += 1


def print_source_code_report(data):
    print('\n########## Source code report ##########\n')
    [print(f'{item[0]} | {item[1]} | {item[2]}') for item in data]


def convert_rst_json(config, base_path, yes=False):
    generate_dir = base_path.joinpath("generate")
    if not prepare_base_directory(generate_dir, yes):
        return
    logging.debug("start converting %s" % generate_dir)
    is_splitted = config.get('chapters_split', False)
    guides_dir, content_dir = prepare_structure(generate_dir)
    transformation_rules, insert_rules = prepare_codio_rules(config)
    workspace_dir = Path(config['workspace']['directory'])
    source_dir = Path(config['workspace']['source'])
    config_path = Path(config['workspace']['json'])
    source_code_type = config.get('opendsa', {}).get('source_code', 'java')
    workout_exercises = get_code_workout_exercises(workspace_dir)
    toc, json_config = get_rst_toc(workspace_dir.joinpath(source_dir),
                                   workspace_dir.joinpath(config_path), workout_exercises)
    source_code_dir = json_config.get('code_dir', '')
    toc, tokens = codio_transformations(toc, transformation_rules, insert_rules)
    book, metadata = make_metadata_items(config)
    chapter = None
    chapter_num = 0
    subsection_num = 0
    logging.debug("convert selected pages")
    refs = OrderedDict()
    label_counter = 0
    tag_directives = list()
    assessments = []
    iframe_images = list()
    source_code_report = list()
    tag_references = prepare_figure_numbers(toc)
    children_containers = [book["children"]]
    lastChapterSection = False

    for ind, item in enumerate(toc):
        if item.section_type == CHAPTER:
            subsection_num = 0
            chapter_num += 1
            slug_name = slugify(item.section_name)
            chapter = item.section_name

            if is_splitted:
                assessments = []
                children_containers = []
                lastChapterSection = False
                book, metadata = make_metadata_items(config)
                book["name"] = item.section_name
                metadata["suppressPageNumbering"] = True
                chapter_dir = generate_dir.joinpath(slug_name.strip('-'))
                guides_dir, content_dir = prepare_structure(chapter_dir)

        else:
            subsection_num += 1
            slug_name = slugify(item.section_name, chapter=chapter)
        logging.debug("convert page {} - {}".format(slug_name, chapter_num))
        converted_md = item.markdown
        if not converted_md:
            label = get_labels(item.lines)
            if label:
                label_counter += 1
                refs[label] = {
                    'pageref': item.section_name
                }

            rst_converter = Rst2Markdown(
                item.lines,
                tag_directives,
                workout_exercises,
                source_code_dir,
                source_code_type,
                tag_references,
                workspace_dir=workspace_dir,
                chapter_num=chapter_num,
                subsection_num=subsection_num
            )
            converted_md = rst_converter.to_markdown()
            assessments += rst_converter.get_assessments()
            iframe_images += rst_converter.get_iframe_images()

            for code_path in rst_converter.get_source_code_paths():
                source_code_report.append(tuple([f'{chapter_num}. {chapter}', item.section_name, code_path]))

            if slug_name in tokens:
                for key, value in tokens.get(slug_name).items():
                    converted_md = converted_md.replace(key, value)

        md_path = content_dir.joinpath(slug_name + ".md")
        section, book_item = make_section_items(item, slug_name, md_path, transformation_rules, converted_md)

        if item.section_type == CHAPTER or item.codio_section == "start":
            book_item["children"] = []
            if item.section_type == CHAPTER:
                children_containers = [children_containers[0]]

        children_containers[len(children_containers) - 1].append(book_item)

        if item.codio_section == "end" and len(children_containers) > 1:
            children_containers.pop()

        if item.section_type == CHAPTER or item.codio_section == "start":
            children_containers.append(book_item["children"])

        section["files"].append({
            "path": "#tabs",
            "action": "close"
        })

        if item.exercise:
            section["files"] = make_odsa_ex_files(item.exercise_path)

        if section:
            metadata["sections"].append(section)

        write_file(md_path, converted_md)

        if is_splitted:
            nextIndex = ind + 1
            lastTocIndex = nextIndex == len(toc)

            if not lastTocIndex and toc[nextIndex].section_type == CHAPTER:
                lastChapterSection = True

            if lastChapterSection or lastTocIndex:
                write_rst_v1_data(guides_dir, metadata, book, assessments)
                continue

    if not is_splitted:
        write_rst_v1_data(guides_dir, metadata, book, assessments)

    process_assets(config, generate_dir, [], [])
    process_iframe_images(config, generate_dir, iframe_images)

    if bool(config.get('opendsa', {}).get('source_code', False)):
        print_source_code_report(source_code_report)


def write_rst_v1_data(guides_dir, metadata, book, assessments):
    code_workout_assessments = list(filter(lambda a: a.type == 'test', assessments))
    create_assessments_data(guides_dir, code_workout_assessments)
    write_metadata(guides_dir, metadata, book)
    write_assessments(guides_dir, assessments)


def convert_rst_toctree(config, base_path, yes=False):
    generate_dir = base_path.joinpath("generate")
    if not prepare_base_directory(generate_dir, yes):
        return
    logging.debug("start converting %s" % generate_dir)
    guides_dir, content_dir = Path(), Path()
    transformation_rules, insert_rules = prepare_codio_rules(config)
    workspace_dir = Path(config['workspace']['directory'])
    source_dir = Path(config['workspace']['rst']).parent
    source_code_type = config.get('opendsa', {}).get('source_code', 'java')
    is_splitted = config.get('chapters_split', False)
    config_path = Path(config['workspace']['rst'])
    toc = get_rst_toc(workspace_dir.joinpath(source_dir), workspace_dir.joinpath(config_path))
    toc, tokens = codio_transformations(toc, transformation_rules, insert_rules)

    chapter = None
    chapter_num = 0
    subsection_num = 0

    logging.debug("convert selected pages")
    refs = OrderedDict()
    label_counter = 0
    tag_directives = list()
    assessments = []
    tag_references = prepare_figure_numbers(toc)
    book = {}
    metadata = {}
    children_containers = []
    chapter_dir = Path()
    lastChapterSection = False

    for ind, item in enumerate(toc):
        if item.section_type == CHAPTER:
            assessments = []
            lastChapterSection = False
            subsection_num = 0
            chapter_num += 1
            slug_name = slugify(item.section_name)
            chapter = item.section_name
            book, metadata = make_metadata_items(config)
            if is_splitted:
                book["name"] = item.section_name
                metadata["suppressPageNumbering"] = True
            children_containers = [book["children"]]
            chapter_dir = generate_dir.joinpath(slug_name.strip('-'))
            if not slug_name:
                print('Chapter name not found', chapter_dir)
                continue
            guides_dir, content_dir = prepare_structure(chapter_dir)
        else:
            subsection_num += 1
            slug_name = slugify(item.section_name, chapter=chapter)
        logging.debug("convert page {} - {}".format(slug_name, chapter_num))
        converted_md = item.markdown
        if not converted_md:
            label = get_labels(item.lines)
            if label:
                label_counter += 1
                refs[label] = {
                    'pageref': item.section_name
                }

            rst_converter = Rst2Markdown(
                item.lines,
                tag_directives,
                {},
                source_code_type,
                tag_references,
                workspace_dir=workspace_dir,
                chapter_num=chapter_num,
                subsection_num=subsection_num
            )
            converted_md = rst_converter.to_markdown()
            assessments += rst_converter.get_assessments()

            if slug_name in tokens:
                for key, value in tokens.get(slug_name).items():
                    converted_md = converted_md.replace(key, value)

        md_path = content_dir.joinpath(slug_name + ".md")
        section, book_item = make_section_items(item, slug_name, md_path, transformation_rules, converted_md)

        if item.section_type == CHAPTER or item.codio_section == "start":
            book_item["children"] = []
            if item.section_type == CHAPTER:
                children_containers = [children_containers[0]]

        children_containers[len(children_containers) - 1].append(book_item)

        if item.codio_section == "end" and len(children_containers) > 1:
            children_containers.pop()

        if item.section_type == CHAPTER or item.codio_section == "start":
            children_containers.append(book_item["children"])

        section["files"].append({
            "path": "#tabs",
            "action": "close"
        })

        if item.exercise:
            exercise_path = Path(item.exercise_path)
            ex_name = exercise_path.stem
            exercise = list(filter(lambda a: a.name == ex_name, assessments))
            if exercise:
                code_file_name = exercise[0].options.get('class_name', '') + '.java'
                code_file_path = str(exercise_path.joinpath(code_file_name))
                section["files"].append({
                    "path": code_file_path,
                    "panel": 0,
                    "action": "open"
                })

        if section:
            metadata["sections"].append(section)

        write_file(md_path, converted_md)

        nextIndex = ind + 1
        lastTocIndex = nextIndex == len(toc)

        if not lastTocIndex and toc[nextIndex].section_type == CHAPTER:
            lastChapterSection = True

        if lastChapterSection or lastTocIndex:
            active_code_exercises = list(filter(lambda a: a.type == ACTIVE_CODE, assessments))
            create_active_code_files(guides_dir, active_code_exercises)
            write_metadata(guides_dir, metadata, book)
            write_assessments(guides_dir, assessments)
            process_assets(config, chapter_dir, [], [])
