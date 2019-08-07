import re

cite_re = re.compile(r"""~?\\cite{(?P<ref>.*?)}""", flags=re.DOTALL + re.VERBOSE)


def make_block(matchobj):
    ref = matchobj.group('ref')
    return '{}'.format(ref)


def convert(input_str):
    return cite_re.sub(make_block, input_str)
