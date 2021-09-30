import re

from converter.rst.assessments.assessment_const import DEFAULT_POINTS, MULTIPLE_CHOICE
from converter.rst.model.assessment_data import AssessmentData


class MultiChoice(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._mchoice_re = re.compile(r"""^( *\.\.\smchoice:: (?P<name>.*?)\n)(?P<options>.*?)\n(?=\S|(?!^$)$)""",
                                      flags=re.MULTILINE + re.DOTALL)
        self._clickablearea_re = re.compile(
            r"""^( *\.\.\sclickablearea:: (?P<name>.*?)\n)(?P<options>.*?)\n(?=\S|(?!^$)$)""",
            flags=re.MULTILINE + re.DOTALL)

    def _mchoice(self, matchobj):
        options = {}
        caret_token = self._caret_token
        name = matchobj.group('name')
        options_group = matchobj.group('options')
        option_re = re.compile(':([^:]+): (.+)')
        options_group_list = options_group.split('\n')
        answers = []
        feedback = []
        for line in options_group.split('\n'):
            opt_match = option_re.match(line.strip())
            if opt_match:
                options_group_list.pop(opt_match.pos)
                if 'answer_' in line:
                    answers.append({opt_match[1]: opt_match[2]})
                    continue
                if 'feedback_' in line:
                    feedback.append({opt_match[1]: opt_match[2]})
                    continue
                options[opt_match[1]] = opt_match[2]

        if answers:
            options['answers'] = answers
            question = [item for item in options_group_list if item.strip() != '']
            options['question'] = '\n'.join(question).strip()
        else:
            options_group = options_group + '\n\n>>>'
            answers_match = re.findall(
                r' +(?P<indent>\s{4})?- +(?P<answer>.*?)(?:\s+)?\s{6} +(?P<correct>[+-])\s+(.*?)\n',
                options_group, flags=re.MULTILINE + re.DOTALL)

            answer_count = 0
            for item in answers_match:
                answer_count += 1
                answer_text = item[0] + item[1]
                answers.append({answer_count: answer_text})
                options['answers'] = answers
                feedback.append(item[3])
                if item[2].strip() == '+':
                    options['correct'] = str(answer_count)

            options_group = re.sub('>>>', '', options_group)
            options_group = re.sub(r':([^:]+): (.+)', '', options_group)
            question = re.sub(r' +(?P<indent>\s{4})?- +(?P<answer>.*?)(?:\s+)?\s{6} +(?P<correct>[+-])\s+(.*?)\n', '',
                              options_group, flags=re.MULTILINE + re.DOTALL)
            question_list = [item.strip() for item in question.split('\n')]
            options['question'] = '\n'.join(question_list).strip()

        if feedback:
            options['feedback'] = feedback

        correct_answer_size = len(options['correct'].split(','))
        if correct_answer_size == 0:
            return
        options['multipleResponse'] = True if correct_answer_size > 1 else False
        options['type'] = 'mchoice'

        name = name.lower().replace('-', '_')
        assessment_id = f'multiple-choice-{name}'
        self._assessments.append(AssessmentData(assessment_id, name, MULTIPLE_CHOICE, DEFAULT_POINTS, options))

        return f'\n{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}\n'

    def _clickablearea(self, matchobj):
        options = {}
        caret_token = self._caret_token
        name = matchobj.group('name')

        if name == 'steptracker_instance_variables':
            test = 0

        options_group = matchobj.group('options')
        option_re = re.compile(':([^:]+):(?: (.+))?')
        options_group_list = options_group.split('\n')
        for line in options_group.split('\n'):
            if line.strip() == '':
                break
            opt_match = option_re.match(line.strip())
            if opt_match:
                options_group_list.pop(opt_match.pos)
                options[opt_match[1]] = opt_match[2]

        answers_str = '\n'.join(options_group_list)
        answers_iscode_match = re.finditer(
            r'^(?P<indent> +).*?:click-(?P<correct>correct|incorrect):(?P<text>.*?):endclick:.*?$',
            answers_str, flags=re.MULTILINE)
        answers_table_match = re.finditer(r' *\|(.*?)\|\n', answers_str)

        answers = []
        if 'iscode' in options:
            for item in answers_iscode_match:
                is_correct = item.group('correct') == 'correct'
                answer = item.group('indent') + item.group(0).strip()
                answer = re.sub(r':click-(?P<correct>correct|incorrect):', '', answer)
                answer = re.sub(r':endclick:', '', answer)
                answers.append({'is_correct': is_correct, 'answer': answer})
        elif 'table' in options:
            correct_answers = options.get('correct', '').split(';')
            for row_num, row in enumerate(answers_table_match, start=1):
                answer_group = row.group(1)
                answer_row = answer_group.split('|')
                for answer_num, answer in enumerate(answer_row, start=1):
                    answer = answer.strip()
                    item_num = f'{row_num},{answer_num}'
                    is_correct = item_num in correct_answers
                    answers.append({'is_correct': is_correct, 'answer': answer})

        options['answers'] = answers
        options['multipleResponse'] = True
        options['type'] = 'clickablearea'

        name = name.lower().replace('-', '_')
        assessment_id = f'multiple-choice-{name}'
        self._assessments.append(AssessmentData(assessment_id, name, MULTIPLE_CHOICE, DEFAULT_POINTS, options))

        return f'\n{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}\n'

    def convert(self):
        output = self.str
        output = self._mchoice_re.sub(self._mchoice, output)
        output = self._clickablearea_re.sub(self._clickablearea, output)
        return output, self._assessments
