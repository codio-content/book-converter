import re


class Epigraph(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._epigraph_re = re.compile(r"""[ ]*\.\. epigraph:: *\n*(?P<content>(?: +[^\n]+\n*)*)""")

    def _epigraph(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        content = content.strip()
        out = []
        for line in content.split('\n'):
            line = line.strip()
            out.append(line)
        content = '\n'.join(out)
        return f'<div style="padding: 10px 30px;">{caret_token}{content}{caret_token}</div>{caret_token}{caret_token}'

    def convert(self):
        output = self.str
        output = self._epigraph_re.sub(self._epigraph, output)
        return output
