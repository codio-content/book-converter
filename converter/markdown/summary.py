import re

summary_re = re.compile(r"""\\begin{summary}(?P<block_contents>.*?)\\end{summary}""", flags=re.DOTALL + re.VERBOSE)


def make_block(matchobj):
    block_contents = matchobj.group('block_contents')
    return '---{}\n---\n'.format(block_contents)


def convert(input_str):
    return summary_re.sub(make_block, input_str)
