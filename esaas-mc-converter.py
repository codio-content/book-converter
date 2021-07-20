import logging
import re
import shutil
import uuid
from argparse import ArgumentParser
from collections import namedtuple
from pathlib import Path

from converter.guides.tools import write_json, read_file, write_file

FileToProcess = namedtuple('FileToProcess', ['name', 'file_name', 'assessment_items'])
AssessmentItem = namedtuple('AssessmentItem', ['type', 'options', 'settings'])

PAGE = 'page'

CHOICE_ANSWER = 'choice_answer'
SELECT_MULTIPLE = 'select_multiple'
FILL_IN_BLANK = 'fill_in'

ASSESSMENT_TYPE = {
    CHOICE_ANSWER: 'multiple-choice',
    SELECT_MULTIPLE: 'multiple-choice',
    FILL_IN_BLANK: 'fill-in-the-blanks'
}


def slugify(in_str):
    return re.sub('[^a-zA-Z0-9]+', '', in_str).lower()


def get_book_item(name, item_type):
    generated_item = {
        "id": slugify(name),
        "title": name,
        "type": item_type,
        'pageId': slugify(name)
    }
    return generated_item


def get_section_item(name, files):
    return {
        "id": slugify(name),
        "title": name,
        "files": files,
        "path": [],
        "type": "markdown",
        "content-file": "",
        "chapter": False,
        "reset": [],
        "teacherOnly": False,
        "learningObjectives": ""
    }


def get_assessment_item(assessment, name, file_name, exercise_num):
    instructions = ''
    guidance = []
    answers = []
    tags = [{
        "name": "Assessment Type",
        "value": "Multiple Choice"
    }, {
        "name": "source",
        "value": file_name
    }]

    for option in assessment.options:
        option = option.strip()
        match_option = re.search(r"(?P<type>tags|group|text|answer|distractor)(?P<value>[ ]%[qQ]{.*?}"
                                 r"(?:,[ ]:explanation[ ]=> .*?\n|\n)|[ ]['\"].*?['\"]\n)", option + '\n',
                                 flags=re.MULTILINE + re.DOTALL + re.VERBOSE)
        if not match_option:
            print(file_name, '- option not match')
            return
        option_type = match_option.group('type')
        option_value = match_option.group('value').strip()

        match_guidance = re.search(r"\s+:explanation => (?P<explanation>.*?)$", option_value, flags=re.MULTILINE)
        if match_guidance:
            guidance.append(match_guidance.group('explanation'))

        if option_type == 'group':
            continue

        if option_type == 'tags':
            tags_list = option_value.split(',')
            for tag in tags_list:
                match_tag = re.search(r"topic:(?P<tag_value>.*?)'$", tag)
                if match_tag:
                    tag = match_tag.group('tag_value')
                    tags.append({'name': 'topic', 'value': tag})
            continue

        option_value = re.sub(r", :explanation => (?P<explanation>.*?)$", "", option_value, flags=re.MULTILINE)
        option_value = re.sub(r"%[qQ]{(.*?)}", r"\1", option_value + '\n', flags=re.MULTILINE + re.DOTALL + re.VERBOSE)
        option_value = option_value.strip().strip('\"')

        if option_type == 'text':
            instructions = option_value
            continue

        if option_type == 'answer' or option_type == 'distractor':
            is_correct = option_type == 'answer'
            answers.append(get_answer(option_value, is_correct))

    if assessment.type == CHOICE_ANSWER or assessment.type == SELECT_MULTIPLE:
        return get_multiple_choice_structure(name, exercise_num, instructions, assessment, answers, guidance, tags)
    if assessment.type == FILL_IN_BLANK:
        return get_fill_in_blank_structure(name, exercise_num, instructions, assessment, answers, guidance, tags)


def get_answer(answer, is_correct):
    return {
        "_id": str(uuid.uuid4()),
        "correct": is_correct,
        "answer": answer.replace("\\n", "\n")
    }


def get_multiple_choice_structure(name, exercise_num, instructions, assessment, answers, guidance, tags):
    correct_answers_count = sum(map(lambda item: item.get('correct'), answers))
    multipleResponse = assessment.type == SELECT_MULTIPLE or correct_answers_count > 1
    return {
        "type": "multiple-choice",
        "taskId": f"multiple-choice-{slugify(name)}-{exercise_num}",
        "source": {
            "name": f"{name} {exercise_num}",
            "showName": True,
            "instructions": instructions.replace("\\n", "\n"),
            "multipleResponse": multipleResponse,
            "isRandomized": assessment.settings.get('randomize', False),
            "answers": answers,
            "guidance": '\n\n'.join(guidance),
            "showGuidanceAfterResponseOption": {
                "type": "Always"
            },
            "showExpectedAnswer": True,
            "points": int(assessment.settings.get('points', 20)),
            "incorrectPoints": 0,
            "arePartialPointsAllowed": False,
            "metadata": {
                "tags": tags,
                "files": [],
                "opened": []
            },
            "bloomsObjectiveLevel": "",
            "learningObjectives": ""
        }
    }


def get_fill_in_blank_structure(name, exercise_num, instructions, assessment, answers, guidance, tags):
    answer = answers[0].get('answer').strip()
    return {
        "type": "fill-in-the-blanks",
        "taskId": f"fill-in-the-blanks-{slugify(name)}-{exercise_num}",
        "source": {
            "name": f"{name} {exercise_num}",
            "showName": True,
            "instructions": instructions.replace("\\n", "\n"),
            "showValues": False,
            "text": f"<<<{answer}>>>",
            "distractors": "",
            "guidance": '\n\n'.join(guidance),
            "showGuidanceAfterResponseOption": {
                "type": "Always"
            },
            "showExpectedAnswer": True,
            "points": int(assessment.settings.get('points', 20)),
            "arePartialPointsAllowed": False,
            "metadata": {
                "tags": tags,
                "files": [],
                "opened": []
            },
            "bloomsObjectiveLevel": "",
            "learningObjectives": "",
            "tokens": {
                "blank": [
                    answer
                ],
                "text": [
                    0
                ],
                "regexPositions": []
            }
        }
    }


def full_book_structure(structure):
    return {
        "name": "ESaaS multiple choice assessments",
        "children": structure
    }


def full_metadata(structure):
    return {
        "theme": "light",
        "scripts": [],
        "lexikonTopic": "",
        "useSubmitButtons": True,
        "useMarkAsComplete": True,
        "sections": structure
    }


def write_section_files(section, output_dir):
    name = section['id']
    content_file = output_dir.joinpath('.guides/content').joinpath(f'{name}.md')
    content_file.parent.mkdir(parents=True, exist_ok=True)
    relative_path = content_file.relative_to(output_dir)
    base_content = section.get('content-file', '')
    write_file(content_file, f'{base_content}\n')
    section['content-file'] = str(str(relative_path).replace("\\", "/"))
    return section


def convert_to_codio_structure(item):
    structure = []
    sections = []
    assessments = []
    files = [
        {
            "action": "close",
            "path": "#tabs"
        }
    ]

    book_item = get_book_item(item.name, PAGE)
    structure.append(book_item)

    content = generate_content(item.name, item.assessment_items)
    current_item = get_section_item(item.name, files)
    current_item['content-file'] = '\n'.join(content)
    sections.append(current_item)

    exercise_num = 0
    for assessment in item.assessment_items:
        exercise_num += 1
        assessments.append(get_assessment_item(assessment, item.name, item.file_name, exercise_num))

    return structure, sections, assessments


def generate_content(assessment_name, assessment_items):
    count = 0
    current_content = []
    for item in assessment_items:
        count += 1
        assessment_type = ASSESSMENT_TYPE[item.type]
        current_content.append(f"{{Check It!|assessment}}({assessment_type}-{slugify(assessment_name)}-{count})\n")
    return current_content


def get_data_to_process(base_directory):
    to_process = []
    for file in (base_directory.glob('*.rb')):
        assessment_items = []

        file_name_without_ext = file.name.rsplit(".", 1)[0]
        file_data = read_file(file.resolve())

        match_quiz_data = re.search(r"^quiz\s+['\"](?P<name>.*?)['\"]\s+(?:do)?\n(?P<assessments_block>.*(?=end))",
                               file_data, flags=re.MULTILINE + re.DOTALL)
        if not match_quiz_data :
            return
        chapter_name = match_quiz_data .group('name').strip()
        assessments_block = match_quiz_data .group('assessments_block')
        assessments_block = re.sub(r"^\s+#+$", "", assessments_block, flags=re.MULTILINE)
        assessments_block += "\n"

        exercise_blocks = re.finditer(r"^\s+(?P<type>choice_answer|select_multiple|fill_in)(?P<settings>\s+:.*? => ?.*?)?\s+do\n"
                             r"(?P<content>.*?)(?:\s+end\s+\n(?!\n\s*\S)|(?=\s+\1))",
                             assessments_block, flags=re.MULTILINE + re.DOTALL + re.VERBOSE)
        if not exercise_blocks:
            print(file, 'PARSE ERROR')
            return
        print(file)

        for item in list(exercise_blocks):
            mc_type = item.group('type')
            content = item.group('content')

            settings = {}
            match_settings = item.group('settings')
            if match_settings is not None:
                for settings_item in match_settings.split(','):
                    match_settings_item = re.search(r":((?P<key>.*?) => (?P<value>.*?))$", settings_item,
                                                    flags=re.MULTILINE)
                    if match_settings_item:
                        settings[match_settings_item.group('key')] = match_settings_item.group('value')

            options = re.findall(r"\s{4}(?:tags|group|text|answer|distractor)(?:[ ]%[qQ]{.*?}"
                                 r"(?:,[ ]:explanation[ ]=> .*?\n|\n)|[ ]['\"].*?['\"]\n)", content + '\n',
                                 flags=re.MULTILINE + re.DOTALL + re.VERBOSE)
            assessment_items.append(AssessmentItem(mc_type, options, settings))

        to_process.append(FileToProcess(chapter_name, file_name_without_ext, assessment_items))
    return to_process


def convert(base_directory, output_dir):
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir()

    for item in get_data_to_process(base_directory):
        structure, sections, assessments = convert_to_codio_structure(item)

        chapter_dir = output_dir.joinpath(item.file_name)
        chapter_dir.mkdir()

        guides_dir = chapter_dir.joinpath('.guides')
        guides_dir.mkdir()

        book_file = guides_dir.joinpath('book.json').resolve()
        write_json(book_file, full_book_structure(structure), False)

        updated_sections = list(map(lambda section: write_section_files(section, chapter_dir), sections))
        metadata_file = guides_dir.joinpath('metadata.json')
        write_json(metadata_file, full_metadata(updated_sections), False)

        assessments_file = guides_dir.joinpath('assessments.json')
        write_json(assessments_file, assessments, False)


def main():
    parser = ArgumentParser(description='Process convert ESaaS MC assessments to Codio MC assessments format.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+', help='path to a sources directory')
    parser.add_argument('-l', '--log', action='store', default=None)
    parser.add_argument('--output', type=str, help='path to output folder')

    args = parser.parse_args()

    logging.basicConfig(filename=args.log, level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname).5s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')

    for path in args.paths:
        convert(Path(path), Path(args.output))


if __name__ == '__main__':
    main()
