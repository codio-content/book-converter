import re

concepts_re = re.compile(r"""\\begin{concepts}(?P<block_contents>.*?)\\end{concepts}""", flags=re.DOTALL + re.VERBOSE)


def make_block(matchobj):
    block_contents = matchobj.group('block_contents')
    return '## Concepts\n{}'.format(block_contents)


def convert(input_str):
    return concepts_re.sub(make_block, input_str)
