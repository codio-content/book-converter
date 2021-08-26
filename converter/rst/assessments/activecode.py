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

        settings = {}
        settings_list = matchobj.group('settings').strip().split('\n')
        for line in settings_list:
            opt_match = re.match(r':([^:]+):(?: +(.+))?', line.strip())
            if opt_match:
                settings[opt_match[1]] = opt_match[2]
        options['settings'] = settings
        options['text'] = matchobj.group('text').strip()

        code = matchobj.group('code')
        class_name_match = re.search(r'public\s+class\s+(?P<name>.*?)(?:<Person>)?\n', code.strip())
        if class_name_match:
            options['class_name'] = class_name_match.group('name')

        options['code'] = code
        options['tests'] = matchobj.group('tests')

        assessment_id = f'test-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, ACTIVE_CODE, DEFAULT_POINTS, options))

        return f'Active code exercise: {name}'

    def convert(self):
        output = self._activecode_re.sub(self._activecode, self.str)
        return output, self._assessments
