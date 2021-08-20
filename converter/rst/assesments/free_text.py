import re

from converter.rst.assesments.assessment_const import DEFAULT_POINTS, FREE_TEXT
from converter.rst.model.assessment_data import AssessmentData


class FreeText(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._poll_re = re.compile(r"""^( *\.\.\spoll:: ?(?P<name>.*?)?\n)(?P<options>.*?)\n(?=\S)""",
                                   flags=re.MULTILINE + re.DOTALL)
        self._shortanswer_re = re.compile(r"""^( *\.\.\sshortanswer:: ?(?P<name>.*?)?\n)(?P<content>.*?)\n(?=\S)""",
                                          flags=re.MULTILINE + re.DOTALL)

    def _poll(self, matchobj):
        options = {}
        caret_token = self._caret_token
        name = matchobj.group('name')
        options_group = matchobj.group('options')
        option_re = re.compile(':([^:]+): (.+)')
        options_group_list = options_group.split('\n')
        for line in options_group.split('\n'):
            opt_match = option_re.match(line.strip())
            if opt_match:
                options_group_list.pop(opt_match.pos)
                options[opt_match[1]] = opt_match[2]

        question = [item.strip() for item in options_group_list if item != '']
        if question:
            options['question'] = question[0]

        assessment_id = f'active-code-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, FREE_TEXT, DEFAULT_POINTS, options))

        return f'{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}'

    def _shortanswer(self, matchobj):
        options = {}
        caret_token = self._caret_token
        name = matchobj.group('name')
        question = matchobj.group('content')
        if question:
            options['question'] = question.strip()
        assessment_id = f'active-code-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, FREE_TEXT, DEFAULT_POINTS, options))

        return f'{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}'

    def convert(self):
        output = self.str
        output = self._poll_re.sub(self._poll, output)
        output = self._shortanswer_re.sub(self._shortanswer, output)
        return output, self._assessments
