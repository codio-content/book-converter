import re

center_re = re.compile(r"""\\begin{center}(?P<block_contents>.*?)\\end{center}""", flags=re.DOTALL + re.VERBOSE)


def make_block(matchobj):
    block_contents = matchobj.group('block_contents')
    block_contents = re.sub(r"\\\\", "<br/>", block_contents, flags=re.MULTILINE)
    return '<center>{}</center>'.format(block_contents)


def convert(input_str):
    return center_re.sub(make_block, input_str)
