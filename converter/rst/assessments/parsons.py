import re

from converter.rst.assessments.assessment_const import DEFAULT_POINTS, PARSONS
from converter.rst.model.assessment_data import AssessmentData


class Parsons(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._parsonsprob_re = re.compile(
            r"""^ *\.\.\sparsonsprob:: (?P<name>.*?\n)(?P<options>.*?)(?P<blocks>\s+-----.*?)\n(?=\S|(?!^$)$)""",
            flags=re.MULTILINE + re.DOTALL)
        self._dragndrop_re = re.compile(
            r"""^( *\.\.\sdragndrop:: (?P<name>.*?)\n)(?P<options>.*?)\n(?=\S|(?!^$)$)""",
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
        blocks_group = f'{blocks_group}\n\n>>>\n\n'
        blocks_match = re.search(r'^\s*-{5}(\n.*?)\n+(?=\S|\n$(?!^$))', blocks_group,
                                 flags=re.MULTILINE + re.DOTALL)
        if blocks_match:
            initial_blocks = ''
            max_distractors = 0
            initial_list = [item.lstrip(' ').lstrip('\n').rstrip() for item in blocks_match.group(1).split('=====')]
            cut_initial_list = self.clean_extra_indention(initial_list)

            for line in cut_initial_list:
                line = line.rstrip().lstrip('\\n').replace('"', '&quot;').replace('\n', '\\n')
                line = line.replace('#paired', '#distractor')
                initial_blocks += f'\\n{line}\n'
                if '#distractor' in line:
                    max_distractors += 1
            options['initial'] = initial_blocks
            options['max_distractors'] = max_distractors

        question = '\n'.join(options_group_list)
        if question:
            question = question.replace('"', '\"').strip()
            options['question'] = question

        name = name.lower().replace('-', '_')
        assessment_id = f'parsons-puzzle-{name}'
        self._assessments.append(AssessmentData(assessment_id, name, PARSONS, DEFAULT_POINTS, options))

        return f'{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}\n'

    def _dragndrop(self, matchobj):
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

        initial_blocks = ''
        question = ''
        matches = [options[item] for item in options if item.startswith('match_')]
        for ind, item in enumerate(matches, start=1):
            match = re.search(r'^(.*?)\|\|\|(.*?)$', item, flags=re.MULTILINE)
            if match:
                initial_blocks += f'{match.group(1)}\n'
                question += f'{ind}. {match.group(2)}\n\n'
        options['question'] = question.replace('"', '\"').strip()
        options['initial'] = initial_blocks

        name = name.lower().replace('-', '_')
        assessment_id = f'parsons-puzzle-{name}'
        self._assessments.append(AssessmentData(assessment_id, name, PARSONS, DEFAULT_POINTS, options))

        return f'{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}\n'

    @staticmethod
    def clean_extra_indention(initial_list):
        str_len = 0
        cut_initial_list = []
        indent_match = re.search(r'^ *', initial_list[0])
        if indent_match:
            str_len = len(indent_match.group(0))
        for ind, item in enumerate(initial_list):
            block = [sub_str[str_len:] for sub_str in item.split('\n')]
            cut_initial_list.append('\n'.join(block))
        return cut_initial_list

    def convert(self):
        output = self.str
        output = self._parsonsprob_re.sub(self._parsonsprob, output)
        output = self._dragndrop_re.sub(self._dragndrop, output)
        return output, self._assessments
