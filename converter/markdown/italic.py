import re

from converter.markdown.block_matcher import match_block


class Italic(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        output = match_block("\\emph{", output, lambda match: f"<i>{match}</i>")
        output = re.sub(r"{\\em[ ](.*?)}", r"<i>\1</i>", output, flags=re.DOTALL)
        output = re.sub(r"{\\it[ ](.*?)}", r"<i>\1</i>", output, flags=re.DOTALL)

        return output
