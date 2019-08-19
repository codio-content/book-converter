import re

from converter.markdown.text_as_paragraph import TextAsParagraph


class Quotation(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

        self._makequotation_re = re.compile(r"""\\makequotation{(?P<block_contents>.*?)}([\s]+)?
                                            {(?P<block_author>.*?)}([ \t]+)?$""",
                                            flags=re.DOTALL + re.VERBOSE + re.MULTILINE)

    def _makequotation_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_author = matchobj.group('block_author')
        block_contents = self.to_paragraph(block_contents)
        caret_token = self._caret_token
        return f'> {block_contents}{caret_token}>{caret_token}> __{block_author}__'

    def convert(self):
        output = self.str
        output = self._makequotation_re.sub(self._makequotation_block, output)

        return output
