import re

from converter.rst.assessments.assessment_const import DEFAULT_POINTS, FREE_TEXT
from converter.rst.model.assessment_data import AssessmentData


class FreeText(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._free_text_re = re.compile(r"""^\.\.[ ]+(poll|shortanswer)::[ ]*(?P<name>.*?)?\n
        (?P<options>(?:[ ]+:[^\n]+\n)+)?(?P<text>.*?)\n(?=\S|(?!^$)[ ]*$)""",
                                        flags=re.MULTILINE + re.DOTALL + re.VERBOSE)

    def _free_text(self, matchobj):
        options = {}
        caret_token = self._caret_token
        name = matchobj.group('name').lower().replace('-', '_')
        options_group = matchobj.group('options')
        options['question'] = matchobj.group('text').strip()

        if options_group:
            option_re = re.compile(':([^:]+): (.+)')
            options_group_list = options_group.split('\n')
            for line in options_group.split('\n'):
                opt_match = option_re.match(line.strip())
                if opt_match:
                    options_group_list.pop(opt_match.pos)
                    options[opt_match[1]] = opt_match[2]

        assessment_id = f'free-text-{name}'
        self._assessments.append(AssessmentData(assessment_id, name, FREE_TEXT, DEFAULT_POINTS, options))

        return f'{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}\n'

    def convert(self):
        output = self.str
        output = self._free_text_re.sub(self._free_text, output)
        return output, self._assessments
