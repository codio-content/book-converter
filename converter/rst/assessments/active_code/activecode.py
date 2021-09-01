import re

from converter.rst.assessments.assessment_const import DEFAULT_POINTS, ACTIVE_CODE
from converter.rst.model.assessment_data import AssessmentData


class ActiveCode(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._activecode_re = re.compile(
            r"""^\.\.\s+activecode:: (?P<name>.*?)\n(?P<content>.*?)\n(?=\S|(?!^$)$)""",
            flags=re.MULTILINE + re.DOTALL + re.VERBOSE)

    def _activecode(self, matchobj):
        name = matchobj.group('name').strip()
        content = matchobj.group('content') + '\n\n'
        options = {}
        class_name = ''
        code = ''
        tests = ''
        text = ''

        settings = {}
        settings_list = re.findall(r'[\t ]+:(?P<key>[^:]+): +(?P<value>.*?)\n', content, flags=re.MULTILINE + re.DOTALL)
        if settings_list:
            for item in settings_list:
                settings[item[0]] = item[1]
            options['settings'] = settings

        content = re.sub(r'^[\t ]+(:[^:]+: +(.*?))\n', '', content, flags=re.MULTILINE + re.DOTALL)

        instructions_match = re.search(r'^\s*(?P<text>.*?)(?:^\s*~~~~\s*\n)', content, flags=re.MULTILINE + re.DOTALL)
        if instructions_match:
            text = instructions_match.group('text').strip()
        content = re.sub(r'^\s*(?P<text>.*?)(?:^\s*~~~~\s*\n)', '', content, flags=re.MULTILINE + re.DOTALL)

        code_match = re.search(r'^(?=\s*public class)(?P<code>.*?)(?=^[\t ]*====)', content,
                               flags=re.MULTILINE + re.DOTALL)
        if code_match:
            code = code_match.group('code')

        tests_match = re.search(r'^\s*====\s*\n(?P<tests>.*?)(?=\n\n$)', content, flags=re.MULTILINE + re.DOTALL)
        if tests_match:
            tests = tests_match.group('tests')

        class_name_re = re.compile(r'^\s*public\s+class\s+(?P<name>.*?)(?:<Person>|extends .*?)?\n', flags=re.MULTILINE)

        if code:
            options['code'] = code
            class_name_match = class_name_re.search(code)
            if class_name_match:
                class_name = class_name_match.group('name').strip()
                options['class_name'] = class_name

        if tests:
            tests = re.sub(r'assertTrue\(passed\);', 'assertTrue(getFinalResults().replace("Starting Tests",'
                                                     '"").replace("Ending Tests",""), passed);', tests)

            constructor = f'\n        public RunestoneTests() {{\n          super("{class_name}");\n       }}\n\n'
            tests = re.sub(r'(.*?public class RunestoneTests extends CodeTestHelper\n *{)\n(.*?)',
                           rf'\1{constructor}\2', tests, flags=re.MULTILINE + re.DOTALL)

            options['tests'] = tests
            test_class_name_match = class_name_re.search(tests)
            if test_class_name_match:
                options['test_class_name'] = test_class_name_match.group('name').strip()

        if text:
            options['text'] = text.strip()

        name = name.replace('-', '_')
        assessment_id = f'test-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, ACTIVE_CODE, DEFAULT_POINTS, options))

        return f'\n\n**See active code exercise: {name}**\n\n'

    def convert(self):
        output = self._activecode_re.sub(self._activecode, self.str)
        return output, self._assessments
