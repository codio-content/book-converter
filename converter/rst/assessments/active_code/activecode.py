import re

from converter.rst.assessments.assessment_const import DEFAULT_POINTS, ACTIVE_CODE
from converter.rst.model.assessment_data import AssessmentData
from converter.rst.utils.clean_indention import clean_indention


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
            text = instructions_match.group('text')
            text = [item.strip() for item in text.split('\n')]
            text = '\n'.join(text)
        content = re.sub(r'^\s*(?P<text>.*?)(?:^\s*~~~~\s*\n)', '', content, flags=re.MULTILINE + re.DOTALL)

        code_match = re.search(r'^(?P<code>.*?)\n(?= *====)|.*?(?=\n^$)', content,
                               flags=re.MULTILINE + re.DOTALL)
        if code_match:
            code = code_match.group('code') or content

        tests_match = re.search(r'[ ]*====[ ]*\n*(?P<tests>.*?)\n(?=[ ]?\S|(?!^$)$)', content, flags=re.DOTALL)

        if tests_match:
            tests = tests_match.group('tests')

        class_name_re = re.compile(r'^\s*public\s+class\s+(?P<name>.*?)(?:<Person>|extends .*?)?\n', flags=re.MULTILINE)

        if code:
            code = clean_indention(code)
            options['code'] = code
            class_name_match = class_name_re.search(code)
            if class_name_match:
                class_name = class_name_match.group('name').strip()
                options['class_name'] = class_name
            else:
                options['class_name'] = 'Main'
        else:
            options['code'] = clean_indention(content)

        if tests:
            has_constructor = re.search(r'public RunestoneTests\(\)', tests)
            if not has_constructor:
                constructor = rf'\1\n\n\2   public RunestoneTests() {{\n\2      super("{class_name}");\n\2   }}\n\n'
                tests = re.sub(r'(( *)public class RunestoneTests extends CodeTestHelper\n? *{)\n',
                               constructor, tests, flags=re.MULTILINE + re.DOTALL)

            options['tests'] = clean_indention(tests)
            test_class_name_match = class_name_re.search(tests)
            if test_class_name_match:
                options['test_class_name'] = test_class_name_match.group('name').strip()

        if text:
            options['text'] = text.strip()

        name = name.replace('-', '_')
        assessment_id = f'test-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, ACTIVE_CODE, DEFAULT_POINTS, options))

        return f'\n\n**See active code exercise: {name}**\n<br>\n'

    def convert(self):
        output = self._activecode_re.sub(self._activecode, self.str)
        return output, self._assessments
