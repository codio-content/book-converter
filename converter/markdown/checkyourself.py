import re

checkyourself_re = re.compile(r"""\\begin{checkyourself}(?P<block_contents>.*?)\\end{checkyourself}""",
                              flags=re.DOTALL + re.VERBOSE)

answer_re = re.compile(r"""\\begin{answer}(?P<answer_block_contents>.*?)\\end{answer}""",
                       flags=re.DOTALL + re.VERBOSE)


def make_answer_block(matchobj):
    answer_block_contents = matchobj.group('answer_block_contents')
    return '<details><summary>Check yourself</summary>{}</details>'.format(answer_block_contents)


def make_block(matchobj):
    block_contents = matchobj.group('block_contents')

    answer_str = answer_re.sub(make_answer_block, block_contents)

    return '|||challenge\n{}\n|||'.format(answer_str)


def convert(input_str):
    return checkyourself_re.sub(make_block, input_str)
