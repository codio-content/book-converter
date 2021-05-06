import re


class IndentedCode(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._indented_code_re = re.compile(
            r"""^(?!\.\. )(?P<text>[^\n]*)::\n+(?P<code>((?P<item>[\t| ]+.*\n)+\n)+)""",
            flags=re.MULTILINE
        )

    def _indented_code(self, matchobj):
        caret_token = self._caret_token
        text = matchobj.group('text')
        text = text.rstrip(':')
        code = matchobj.group('code')
        colon = ':' if text else ''
        return f'{caret_token}{text}{colon}{caret_token}{caret_token}```{code.strip()}```' \
               f'{caret_token}{caret_token}'

    def convert(self):
        output = self.str
        output = self._indented_code_re.sub(self._indented_code, output)
        return output
