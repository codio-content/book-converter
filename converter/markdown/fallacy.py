import re

from converter.markdown.text_as_paragraph import TextAsParagraph

fallacy_re = re.compile(r"""\\begin{fallacy}{(?P<title>.*?)}(?P<block_contents>.*?)\\end{fallacy}""",
                        flags=re.DOTALL + re.VERBOSE)


class Fallacy(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = self.to_paragraph(block_contents)
        block_contents = block_contents.replace('\n', ' ')
        title = matchobj.group('title')
        title = self.to_paragraph(title)
        caret_token = self._caret_token
        return f'{caret_token}## {title}{caret_token}{block_contents}'

    def convert(self):
        return fallacy_re.sub(self.make_block, self.str)
