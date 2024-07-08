import re

from converter.markdown.block_matcher import match_block
from converter.markdown.text_as_paragraph import TextAsParagraph

competency_re = re.compile(r"""\\competency(\[(.*?)\])?{(?P<block_contents>.*?)}""",
                              flags=re.DOTALL + re.VERBOSE)

class Competency(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = re.sub(r"\s*\n\s*", " ", block_contents).strip()
        block_contents = block_contents.replace("\\\\", "<br/>")
        caret_token = self._caret_token
        return f'{caret_token}|||topic{caret_token}## Competency{caret_token}{block_contents}{caret_token}{caret_token}|||{caret_token}'

    def convert(self):
        return competency_re.sub(self.make_block, self.str)