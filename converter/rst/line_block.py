import re


class LineBlock(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._lineblock_re = re.compile(r"""^((?: {2,})?\| )[^\n]*(?:\n(?:\1| {2,})[^\n]+)*""", flags=re.MULTILINE)

    def _lineblock(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group(0)
        content = re.sub(r'^( *\| ?| {2,})', '', content, flags=re.MULTILINE)
        out = []
        for line in content.split('\n'):
            line = line.strip()
            out.append(f' {line}')
        content = '\n'.join(out)
        return f' <div style="padding-left: 50px;">{caret_token}{content}{caret_token} </div>{caret_token}'

    def convert(self):
        output = self.str
        output = self._lineblock_re.sub(self._lineblock, output)
        return output
