import re


class Definition(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._definition_re = re.compile(
            r"""^(?!\s|\d\. |#\. |\* |- |\.\. ):?(?P<term>[^\n]+)\n(?P<content> {2,}[^\n]+(?:\n {2,}[^\n]+\s*)*\n+)""",
            flags=re.MULTILINE
        )

    def _definition(self, matchobj):
        caret_token = self._caret_token
        term = matchobj.group('term')
        term = term.strip('**').strip()
        content = matchobj.group('content')

        space = re.search('\n *', content)
        space_count = len(space.group(0)) - 1
        space_regex = f"\n^ {{{space_count}}}"
        content = re.sub(space_regex, '', content, flags=re.MULTILINE)

        lines = content.split('\n')
        out = []
        for line in lines:
            out.append(f'{line.strip()}{caret_token}')
        content = '\n'.join(out)
        return f'{caret_token}{caret_token}**{term}**{caret_token}{content}{caret_token}{caret_token}'

    def convert(self):
        output = self.str
        output = self._definition_re.sub(self._definition, output)
        return output
