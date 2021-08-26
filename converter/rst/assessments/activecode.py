import re

from converter.rst.assessments.assessment_const import DEFAULT_POINTS, ACTIVE_CODE
from converter.rst.model.assessment_data import AssessmentData


class ActiveCode(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._activecode_re = re.compile(
            r"""^\s*\.\.\sactivecode:: (?P<name>.*?)\n(?P<settings>^[\t ]+:[^:]+: +.*?^$)+\n(?P<text>.*?)
            \s*~~~~\s*\n(?P<code>.*?)\s*====\s*\n(?P<tests>.*?)\n(?=\S)""", flags=re.MULTILINE + re.DOTALL + re.VERBOSE)

    def _activecode(self, matchobj):
        options = {}
        name = matchobj.group('name').strip()
        code = matchobj.group('code')
        tests = matchobj.group('tests')

        settings = {}
        settings_list = matchobj.group('settings').strip().split('\n')
        for line in settings_list:
            opt_match = re.match(r':([^:]+):(?: +(.+))?', line.strip())
            if opt_match:
                settings[opt_match[1]] = opt_match[2]
        options['settings'] = settings
        options['text'] = matchobj.group('text').strip()
        options['code'] = code
        options['tests'] = tests

        class_name_re = re.compile(r'public\s+class\s+(?P<name>.*?)(?:<Person>|extends .*?)?\n')
        class_name_match = class_name_re.search(code.strip())
        if class_name_match:
            options['class_name'] = class_name_match.group('name')
        test_class_name_match = class_name_re.search(tests.strip())
        if test_class_name_match:
            options['test_class_name'] = test_class_name_match.group('name')

        assessment_id = f'test-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, ACTIVE_CODE, DEFAULT_POINTS, options))

        return f'Active code exercise: {name}'

    def convert(self):
        output = self._activecode_re.sub(self._activecode, self.str)
        return output, self._assessments
