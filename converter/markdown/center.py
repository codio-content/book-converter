import re

from converter.markdown.text_as_paragraph import TextAsParagraph

center_re = re.compile(r"""\\begin{(center|centering)}(?P<block_contents>.*?)\\end{(center|centering)}""",
                       flags=re.DOTALL + re.VERBOSE)


class Center(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = re.sub(r"\\\\", "<br/>", block_contents, flags=re.MULTILINE)
        block_contents = self.to_paragraph(block_contents)
        caret_token = self._caret_token
        return f'<center>{caret_token}{block_contents}{caret_token}</center>'

    def convert(self):
        return center_re.sub(self.make_block, self.str)
