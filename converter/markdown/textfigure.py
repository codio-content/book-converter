import re

from converter.markdown.text_as_paragraph import TextAsParagraph


class Textfigure(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)
        self.str = latex_str
        self._textfigure_re = re.compile(r"""\\begin{textfigure}(?P<block_contents>.*?)\\end{textfigure}""",
                                         flags=re.DOTALL)

    def _textfigure_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = self.to_paragraph(block_contents)

        return f'{block_contents}'

    def convert(self):
        output = self.str
        output = self._textfigure_re.sub(self._textfigure_block, output)

        return output
