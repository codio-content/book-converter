import re


class CodeBlock(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._code_block_re = re.compile(r""" *\.\. +code-block:: ?(?P<lang>.*?)?\n\s*\n(?P<content>.*?)\n(?=\S|^$)""",
                                         flags=re.MULTILINE + re.DOTALL)

    def _code_block(self, matchobj):
        lang = matchobj.group('lang').strip()
        content = matchobj.group('content').rstrip()

        return f'\n ``` {lang}\n{content}\n ```\n'

    def convert(self):
        output = self._code_block_re.sub(self._code_block, self.str)
        return output
