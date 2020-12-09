import logging
import re
import subprocess

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
        write_assessment_files(exercise_data, generate_dir, odsa_private_dir)


def write_assessment_files(exercise_data, generate_dir, odsa_private_dir):
    group_name = exercise_data.get('dir_name', None)
    file_name = exercise_data.get('file_name', None)
    if group_name is None or file_name is None:
        return

    private_group_dir_path = odsa_private_dir.joinpath(group_name)
    private_group_dir_path.mkdir(exist_ok=True, parents=True)
    data_dir = private_group_dir_path.joinpath(file_name)
    data_dir.mkdir(exist_ok=True, parents=True)

    starter_code_dir = generate_dir.joinpath(f'exercises/{group_name}/{file_name}')
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
        run_tests += get_run_tests_code(passed_data, failed_data, message, num)
        unit_tests += get_unit_tests_code(actual, expected, method_name, class_name, num)

    code = f'import java.util.Objects;\n' \
           f'import java.util.concurrent.Callable;\n' \
           f'\n' \
           f'public class Tester {{\n' \
           f'   public static void main(String[] args) {{\n' \
           f'       int total_tests = {num};\n' \
           f'       int passed_tests = 0;\n' \
           f'       String feedback = "";\n' \
           f'       String method_name = "{method_name}";\n' \
           f'\n' \
           f'{run_tests}' \
           f'       String total = "" + total_tests;\n' \
           f'       String passed = "" + passed_tests;\n' \
           f'       String output = total + "\\n" + passed + "\\n" + method_name + "\\n" + feedback;\n' \
           f'       System.out.println(output);\n' \
           f'   }}\n' \
           f'\n' \
           f'   private static boolean runTest(Callable<Boolean> func) {{\n' \
           f'       try {{\n' \
           f'           return func.call();\n' \
           f'       }} catch (Exception | Error e) {{\n' \
           f'           return false;\n' \
           f'       }}\n' \
           f'   }}\n\n' \
           f'{unit_tests}' \
           f'}}\n'
    return code, '\n'.join(static_checks)


def get_unit_tests_code(actual, expected, method_name, class_name, num):
    return f'   public static class Test{num} implements Callable<Boolean>{{\n' \
           f'       private static final {class_name} instance = new {class_name}();\n' \
           f'\n' \
           f'       public Test{num}() {{\n' \
           f'       }}\n' \
           f'\n' \
           f'       public static Object getExpectedVal() {{\n' \
           f'          return {expected};\n' \
           f'       }}\n' \
           f'\n' \
           f'       public static Object getActualVal() {{\n' \
           f'          return instance.{method_name}({actual});\n' \
           f'       }}\n' \
           f'\n' \
           f'       public Boolean call() {{\n' \
           f'          return Objects.equals(getExpectedVal(), getActualVal());\n' \
           f'       }}\n' \
           f'   }}\n' \
           f'\n'


def get_run_tests_code(passed_data, failed_data, message, num):
    new_regex = re.compile(r'new\s+[a-zA-Z0-9]+(\s*\[\s*])+\s*')
    passed_data = passed_data.replace('"', '\\"')
    failed_data = failed_data.replace('"', '\\"')
    passed_data = new_regex.sub('', passed_data)
    failed_data = new_regex.sub('', failed_data)
    return f'       if (runTest(new Test{num}())) {{\n' \
           f'           passed_tests++;\n' \
           f'           feedback += "{message}Test <span style=\\"color:green\\"><b>PASSED</b></span>' \
           f'{passed_data}\\n\\n";\n' \
           f'       }} else {{\n' \
           f'           feedback += "{message}Test <span style=\\"color:red\\"><b>FAILED</b></span>' \
           f'{failed_data}\\n";\n' \
           f'           try {{\n' \
           f'               Object exp = Test{num}.getExpectedVal();\n' \
           f'               Object act = Test{num}.getActualVal();\n' \
           f'               feedback += "Expected: " + exp + "\\n" + "but was: " + act + "\\n\\n";\n' \
           f'           }} catch (Exception | Error e) {{\n' \
           f'               feedback += e + "\\n\\n";\n' \
           f'           }}\n' \
           f'       }}\n' \
           f'\n'
