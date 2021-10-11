import re


class LineBlock(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._lineblock_re = re.compile(r"""\.\. line-block::[ ]*\n(?P<content>(?:[^\n]+\n)+)(?=^$)""",
                                        flags=re.MULTILINE)

    def _lineblock(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        content = content.rstrip().replace('``', '')
        out = [f' {line.strip()}' for line in content.split('\n')]
        content = '\n'.join(out)
        return f'\n<pre>{content}{caret_token}</pre>{caret_token}{caret_token}\n'

    def convert(self):
        output = self.str
        output = self._lineblock_re.sub(self._lineblock, output)
        return output
