import re

from converter.rst.assesments.assessment_const import DEFAULT_POINTS, PARSONS
from converter.rst.model.assessment_data import AssessmentData


class Parsons(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._parsonsprob_re = re.compile(
            r"""^( *\.\.\sparsonsprob:: (?P<name>.*?\n)(?P<options>.*?)(?P<blocks>\s+-----.*?)\n(?=\S|(?!^$)$))""",
            flags=re.MULTILINE + re.DOTALL)

    def _parsonsprob(self, matchobj):
        options = {}
        caret_token = self._caret_token
        name = matchobj.group('name').strip()
        options_group = matchobj.group('options')
        option_re = re.compile(r':([^:]+):(?: +(.+))?')
        options_group_list = options_group.split('\n')
        for line in options_group.split('\n'):
            opt_match = option_re.match(line.strip())
            if opt_match:
                options_group_list.pop(opt_match.pos)
                options[opt_match[1]] = opt_match[2]

        blocks_group = matchobj.group('blocks')
        blocks_match = re.search(r'^\s*-{5}(\n.*?)\n$', f'{blocks_group}\n', flags=re.MULTILINE + re.DOTALL)
        if blocks_match:
            initial_list = blocks_match.group(1).split('=====')
            initial_blocks = ''
            max_distractors = 0
            for line in initial_list:
                line = line.rstrip().replace('\n', '\\n').replace('"', '&quot;')
                line = line.replace('#paired', '#distractor')
                initial_blocks += f'{line}\n'
                if '#distractor' in line:
                    max_distractors += 1
            options['initial'] = initial_blocks
            options['max_distractors'] = max_distractors

        question = '\n'.join(options_group_list)
        if question:
            question = question.replace('"', '\"').strip()
            options['question'] = question

        assessment_id = f'parsons-puzzle-{name.lower()}'
        self._assessments.append(AssessmentData(assessment_id, name, PARSONS, DEFAULT_POINTS, options))

        return f'{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}\n'

    def convert(self):
        output = self._parsonsprob_re.sub(self._parsonsprob, self.str)
        return output, self._assessments
