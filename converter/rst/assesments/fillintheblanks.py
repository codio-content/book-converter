import re

from converter.rst.assesments.assessment_const import DEFAULT_POINTS, FILL_IN_THE_BLANKS
from converter.rst.model.assessment_data import AssessmentData


class FillInTheBlanks(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._fillintheblanks_re = re.compile(
            r"""^( *\.\.\sfillintheblank:: ?(?P<name>.*?)?\n)(?P<options>.*?)\n(?=\S|\s+\n)""",
            flags=re.MULTILINE + re.DOTALL)

    def _fillintheblanks(self, matchobj):
        options = {}
        caret_token = self._caret_token
        name = matchobj.group('name')
        options_group = matchobj.group('options')
        option_re = re.compile('\s+(?P<correct>-)?\s+:(?P<key>[^:]+): (?P<value>.+)')
        options_group_list = options_group.split('\n')
        feedback = []
        correct_answers = {}
        for line in options_group.split('\n'):
            opt_match = option_re.match(line)
            if opt_match:
                key = opt_match.group('key')
                value = opt_match.group('value')
                if key == '.*':
                    feedback.append(value)
                    options_group_list.pop(opt_match.lastindex)
                    continue
                options_group_list.pop(opt_match.lastindex)
                correct_answers[key] = value
                options['correct_answers'] = correct_answers

        text = [item.strip() for item in options_group_list if item != '']
        if text:
            options['text'] = text[0]
        if feedback:
            options['feedback'] = feedback

        assessment_id = f'fill-in-the-blanks-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, FILL_IN_THE_BLANKS, DEFAULT_POINTS, options))

        return f'{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}'

    def convert(self):
        output = self._fillintheblanks_re.sub(self._fillintheblanks, self.str)
        return output, self._assessments
