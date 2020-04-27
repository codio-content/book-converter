import re

from converter.markdown.text_as_paragraph import TextAsParagraph

elaboration_re = re.compile(r"""(\s+)?\\begin{elaboration}{(?P<title>.*?)}(?P<block_contents>.*?)\\end{elaboration}""",
                            flags=re.DOTALL + re.VERBOSE)


class Elaboration(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        title = matchobj.group('title')
        title = self.to_paragraph(title)
        block_contents = self.to_paragraph(block_contents)
        caret_token = self._caret_token
        return f'{caret_token}## {title}{caret_token}{block_contents}'

    def convert(self):
        return elaboration_re.sub(self.make_block, self.str)
