import re

from converter.markdown.block_matcher import match_block


class Bold(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        escaped_asterisk = "\\*"
        output = re.sub(r"\\textbf{(.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"{\\bf[ ](.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"{\\sf[ ](.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)

        output = match_block("\\B{", output, lambda match: f"**{match}**")
        output = match_block("\\C{", output, lambda match: f"__{match}__")
        output = match_block("\\T{", output, lambda match: f"**{match.strip().replace('*', escaped_asterisk)}**")

        return output
