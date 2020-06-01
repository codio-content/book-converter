import re

from converter.markdown.text_as_paragraph import TextAsParagraph

chips_re = re.compile(r"""\\begin{chips}{(?P<title>.*?)}{(?P<ref>.*?)}(?P<block_contents>.*?)\\end{chips}""",
                      flags=re.DOTALL)


class Chips(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = self.to_paragraph(block_contents)
        title = matchobj.group('title')
        title = self.to_paragraph(title)
        ref = matchobj.group('ref')
        caret_token = self._caret_token
        return f'## {title}{caret_token}{ref}{caret_token}{block_contents}{caret_token}'

    def convert(self):
        return chips_re.sub(self.make_block, self.str)
