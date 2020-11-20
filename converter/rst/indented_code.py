import re


class IndentedCode(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._indented_code_re = re.compile(
            r"""^(?!\.\. )(?P<text>[^\n]*)::\n+(?P<code>(?P<indent> {2,})(?:[^\n]+\n)*)""",
            flags=re.MULTILINE
        )

    def _indented_code(self, matchobj):
        caret_token = self._caret_token
        text = matchobj.group('text')
        text = text.rstrip(':')
        indent = matchobj.group('indent')
        code = matchobj.group('code')
        space = len(indent)
        space_re = f"^ {{{space}}}"
        colon = ':' if text else ''
        code = re.sub(space_re, '', code.strip(), flags=re.MULTILINE) if space else code.strip()
        return f'{caret_token}{text}{colon}{caret_token}{caret_token}```{caret_token}{code}{caret_token}```' \
               f'{caret_token}{caret_token}'

    def convert(self):
        output = self.str
        output = self._indented_code_re.sub(self._indented_code, output)
        return output
