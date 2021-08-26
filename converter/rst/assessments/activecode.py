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
        content = matchobj.group('content')
        options_match = re.search(
            r'(?P<settings>^[\t ]+:[^:]+:[ ]+.*?^\s*$)+\n(?:(?P<text>.*?)\s*~~~~\s*\n)?(?:(?P<code>.*?)'
            r'\s*====\s*\n)?(?P<tests>.*?)(?=\n\n^$)', content + '\n\n',
            flags=re.MULTILINE + re.DOTALL + re.VERBOSE)

        if not options_match:
            return

        options = {}
        code = options_match.group('code')
        tests = options_match.group('tests')
        text = options_match.group('text')

        class_name_re = re.compile(r'\s*public\s+class\s+(?P<name>.*?)(?:<Person>|extends .*?)?\n')

        if code:
            options['code'] = code
            class_name_match = class_name_re.search(code)
            if class_name_match:
                options['class_name'] = class_name_match.group('name').strip()

        if tests:
            tests = re.sub(r'assertTrue\(passed\);', 'assertTrue(getFinalResults().replace("Starting Tests ",'
                                                     '"").replace(" Ending Tests",""), passed);', tests)
            options['tests'] = tests
            test_class_name_match = class_name_re.search(tests)
            if test_class_name_match:
                options['test_class_name'] = test_class_name_match.group('name').strip()

        if text:
            options['text'] = text.strip()

        settings = {}
        settings_list = options_match.group('settings').strip().split('\n')
        for line in settings_list:
            opt_match = re.match(r':([^:]+):(?: +(.+))?', line.strip())
            if opt_match:
                settings[opt_match[1]] = opt_match[2]
        options['settings'] = settings

        assessment_id = f'test-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, ACTIVE_CODE, DEFAULT_POINTS, options))

        return f'**Active code exercise: {name}**'

    def convert(self):
        output = self._activecode_re.sub(self._activecode, self.str)
        return output, self._assessments
