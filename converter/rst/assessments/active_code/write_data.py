import logging
import shutil
import subprocess
from pathlib import Path

from converter.guides.tools import write_file, read_file


def create_active_code_files(guides_dir, exercises):
    if not exercises:
        return
    logging.debug('process create active code test assessments data')

    data_files = set()
    tests_dir = guides_dir.joinpath('secure/active_code')
    tests_dir.mkdir(exist_ok=True, parents=True)

    for exercise in exercises:
        options = exercise.options
        exercise_name = exercise.name
        class_name = options.get('class_name', '')
        test_class_name = options.get('test_class_name', '')
        class_code = options.get('code', '')
        tests_code = options.get('tests', '')
        settings = options.get('settings', {})
        data_file = settings.get('datafile', None)

        if data_file:
            files = data_file.split(',')
            for file in files:
                data_files.add(file.strip())

        if tests_code:
            private_exercise_dir = tests_dir.joinpath(exercise_name)
            private_exercise_dir.mkdir(exist_ok=True, parents=True)
            test_file = private_exercise_dir.joinpath(f'{test_class_name}.java')
            write_file(test_file, tests_code)

        code_dir = guides_dir.joinpath(f'active_code/{exercise_name}')
        code_dir.mkdir(exist_ok=True, parents=True)
        code_file = code_dir.joinpath(f'{class_name}.java')
        write_file(code_file, class_code)

    write_static_files(guides_dir)


def write_static_files(guides_dir):
    lib_dir = guides_dir.joinpath('lib')
    lib_dir.mkdir(exist_ok=True, parents=True)
    shutil.copy(Path('converter/rst/assessments/active_code/CodeTestHelper.java'), lib_dir)
    shutil.copy(Path('converter/rst/assessments/active_code/junit-4.13.1.jar'), lib_dir)
    shutil.copy(Path('converter/rst/assessments/active_code/hamcrest-core-1.3.jar'), lib_dir)
    shutil.copy(Path('converter/rst/assessments/active_code/turtleClasses.jar'), lib_dir)

    tests_dir = guides_dir.joinpath('secure/active_code')
    run_script_data = read_file(Path('converter/rst/assessments/active_code/run.script'))
    write_file(Path(f'{tests_dir}/run.py'), run_script_data)
    subprocess.call(f'chmod +x {tests_dir}/run.py', shell=True)
