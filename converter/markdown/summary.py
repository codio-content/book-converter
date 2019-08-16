import re

from converter.markdown.text_as_paragraph import TextAsParagraph

summary_re = re.compile(r"""\\begin{summary}(?P<block_contents>.*?)\\end{summary}""", flags=re.DOTALL + re.VERBOSE)


class Summary(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = self.to_paragraph(block_contents)
        caret_token = self._caret_token
        return f"---{caret_token}{block_contents}{caret_token}{caret_token}---{caret_token}"

    def convert(self):
        return summary_re.sub(self.make_block, self.str)
