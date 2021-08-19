import re

from converter.rst.assesments.assessment_const import DEFAULT_POINTS, MULTIPLE_CHOICE
from converter.rst.model.assessment_data import AssessmentData


class MultiChoice(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._mchoice_re = re.compile(r"""^( *\.\.\smchoice:: ?(?P<name>.*?)?\n)(?P<options>.*?)\n(?=\S|\s+\n)""",
                                      flags=re.MULTILINE + re.DOTALL)

    def _mchoice(self, matchobj):
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

        assessment_id = f'multiple-choice-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, MULTIPLE_CHOICE, DEFAULT_POINTS, options))

        return f'{caret_token}{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}{caret_token}'

    def convert(self):
        output = self._mchoice_re.sub(self._mchoice, self.str)
        return output, self._assessments
