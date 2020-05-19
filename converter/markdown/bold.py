import re

from converter.markdown.block_matcher import match_block


def make_content(line, chars):
    line = re.sub(r'\\B{(.*?)}', r'\1', line)
    line = re.sub(r'\\C{(.*?)}', r'\1', line)
    line = re.sub(r'\\T{(.*?)}', r'\1', line)
    line = line.replace('*', '\\*')
    line = line.strip()
    return f"{chars}{line}{chars}"


class Bold(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        output = re.sub(r"\\textbf{(.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"{\\bf[ ](.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"{\\sf[ ](.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)

        output = match_block("\\B{", output, lambda match: f"{make_content(match, '**')}")
        output = match_block("\\C{", output, lambda match: f"{make_content(match, '__')}")
        output = match_block("\\T{", output, lambda match: f"{make_content(match, '**')}")

        return output
