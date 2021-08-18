import re


class CodeBlock(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._code_block_re = re.compile(r"""^( *\.\.\scode-block:: ?(?P<lang>.*?)?\n)(?P<content>.*?)\n(?=\S)""",
                                         flags=re.MULTILINE + re.DOTALL)

    def _code_block(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        lang = matchobj.group('lang').strip()
        return f'{caret_token}``` {lang}{caret_token}{content}{caret_token}```{caret_token}{caret_token}\n'

    def convert(self):
        output = self._code_block_re.sub(self._code_block, self.str)
        return output
