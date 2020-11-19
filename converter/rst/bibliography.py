import re


class Bibliography(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._bib_re = re.compile(r"""^\.\. (?P<label>\[[a-zA-z\d]+])\n*(?P<text>(?:\s+[^\n]+\n*)*)""",
                                  flags=re.MULTILINE)

    @staticmethod
    def _bib(matchobj):
        label = matchobj.group('label')
        text = matchobj.group('text')
        out = []
        for line in text.split('\n'):
            line = line.strip()
            out.append(line)
        text = ' '.join(out)
        return f'{label.strip()} {text.strip()}'

    def convert(self):
        output = self.str
        output = self._bib_re.sub(self._bib, output)
        return output
