import re

elaboration_re = re.compile(r"""\\begin{elaboration}{(?P<title>.*?)}(?P<block_contents>.*?)\\end{elaboration}""",
                            flags=re.DOTALL + re.VERBOSE)


def make_block(matchobj):
    block_contents = matchobj.group('block_contents')
    title = matchobj.group('title')
    title = re.sub(r"\n", " ", title)
    return '## {}\n{}'.format(title, block_contents)


def convert(input_str):
    return elaboration_re.sub(make_block, input_str)
