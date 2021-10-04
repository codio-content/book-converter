import logging
import os
import re
import subprocess
from string import Template

from converter.guides.tools import read_file, write_file, parse_csv_lines


def create_assessments_data(guides_dir, generate_dir, exercises):
    if not exercises:
        return
    logging.debug("process create odsa test assessments content")
    odsa_private_dir = guides_dir.joinpath("secure/assessments")
    odsa_private_dir.mkdir(exist_ok=True, parents=True)

    run_file_path = odsa_private_dir.joinpath('run.py')
    run_file_data = read_file('converter/opendsa_assessments/run.script')
    write_file(run_file_path, run_file_data)
    subprocess.call(f'chmod +x {run_file_path}', shell=True)

    for exercise in exercises:
        exercise_data = exercises[exercise]
        write_assessment_files(exercise_data, guides_dir, odsa_private_dir)


def write_assessment_files(exercise_data, guides_dir, odsa_private_dir):
    group_name = exercise_data.get('dir_name', None)
    file_name = exercise_data.get('file_name', None)
    if group_name is None or file_name is None:
        return

    private_group_dir_path = odsa_private_dir.joinpath(group_name)
    private_group_dir_path.mkdir(exist_ok=True, parents=True)
    data_dir = private_group_dir_path.joinpath(file_name)
    data_dir.mkdir(exist_ok=True, parents=True)

    starter_code_dir = guides_dir.parent.joinpath(f'exercises/{group_name}/{file_name}')
    starter_code_dir.mkdir(exist_ok=True, parents=True)

    wrapper_code_path = data_dir.joinpath('wrapper_code.java')
    starter_code_path = starter_code_dir.joinpath('starter_code.java')
    tester_code_path = data_dir.joinpath('Tester.java')
    static_checks_path = data_dir.joinpath('static_checks')

    wrapper_code = exercise_data['wrapper_code']
    starter_code = exercise_data['starter_code']
    starter_code = starter_code.replace("___", "// Write your code below")
    tester_code, static_checks = get_tester_code(exercise_data)

    write_file(tester_code_path, tester_code)
    write_file(wrapper_code_path, wrapper_code)
    write_file(starter_code_path, starter_code)
    write_file(static_checks_path, static_checks)


def get_parsed_tests(exercise_data):
    parsed_tests = parse_csv_lines(exercise_data.get('tests', ''))
    return [item for item in parsed_tests if len(item)]


def parse_description_specifier(desc):
    match = re.search(r"(?:(?:(example|hidden|static)\s*:\s*)+)(.*)", desc.strip())
    if match:
        desc = match[1].strip()
    return desc


def get_tester_code(exercise_data):
    if not exercise_data:
        return ''
    num = 0
    run_tests = ''
    unit_tests = ''
    static_checks = []
    class_name = exercise_data.get('class_name', '')
    method_name = exercise_data.get('method_name', '')
    parsed_tests = get_parsed_tests(exercise_data)

    for test in parsed_tests:
        actual = test[0]
        expected = test[1]
        expected = expected.strip()
        message = ''

        passed_data = f': {method_name}({actual}) -> {expected}'
        failed_data = f': {method_name}({actual})'

        if len(test) >= 3:
            desc = parse_description_specifier(test[2])
            if desc == 'static':
                static_checks.append('|||'.join(test))
                continue
            if desc == 'example':
                message = ''
            elif desc == 'hidden':
                passed_data = ': hidden test'
                failed_data = ': hidden test'
            else:
                message = desc.strip('"')
                message = f'{message}\\n\\n'
                passed_data = ''
                failed_data = ''
        num += 1
        run_tests += get_run_test_code(passed_data, failed_data, message, num)
        unit_tests += get_unit_test_code(actual, expected, method_name, class_name, num)

    dict_for_tester_code = dict(num=num,
                                method_name=method_name,
                                run_tests=run_tests,
                                unit_tests=unit_tests)
    tester_code_tpl = read_template('templates/tester_code_tpl.java')
    tester_code = Template(tester_code_tpl).substitute(dict_for_tester_code)
    return tester_code, '\n'.join(static_checks)


def get_unit_test_code(actual, expected, method_name, class_name, num):
    dict_for_unit_test_code = dict(num=num,
                                   class_name=class_name,
                                   expected=expected,
                                   method_name=method_name,
                                   actual=actual)
    unit_test_code_tpl = read_template('templates/unit_test_code_tpl.java')
    return Template(unit_test_code_tpl).substitute(dict_for_unit_test_code)


def get_run_test_code(passed_data, failed_data, message, num):
    new_regex = re.compile(r'new\s+[a-zA-Z0-9]+(\s*\[\s*])+\s*')
    passed_data = passed_data.replace('"', '\\"')
    failed_data = failed_data.replace('"', '\\"')
    passed_data = new_regex.sub('', passed_data)
    failed_data = new_regex.sub('', failed_data)

    dict_for_run_test = dict(num=num,
                             message=message,
                             passed_data=passed_data,
                             failed_data=failed_data)
    run_test_code_tpl = read_template('templates/run_test_code_tpl.java')
    return Template(run_test_code_tpl).substitute(dict_for_run_test)


def read_template(relative_path):
    current_dirname = os.path.dirname(__file__)
    with open(os.path.join(current_dirname, relative_path)) as file:
        return file.read()
