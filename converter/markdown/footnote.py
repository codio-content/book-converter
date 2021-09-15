import re


class Footnote(object):
    def __init__(self, latex_str):
        self.str = latex_str
        self._count = 0
        self._footnotes = []
        self._footnote_mark_re = re.compile(r"""\\footnotemark{}""")
        self._footnote_text_re = re.compile(r"""\\footnotetext{\n(?P<text>.*?)^}$""", flags=re.MULTILINE + re.DOTALL)
        self._footnote_re = re.compile(r"""\\footnote{(?P<text>.*?)(?<!\\)}""")

    def _footnote_mark(self, matchobj):
        self._count += 1
        return f'<b style="color: blue">[{self._count}]</b>'

    def _footnote_text(self, matchobj):
        self._count += 1
        text = matchobj.group('text')
        self._footnotes.append(f'<b style="color: blue">[{self._count}]</b> {text}')
        return ''

    def _footnote(self, matchobj):
        self._count += 1
        text = matchobj.group('text')
        self._footnotes.append(f'<b style="color: blue">[{self._count}]</b> {text}')
        return f'<b style="color: blue">[{self._count}]</b>'

    def convert(self):
        output = self.str
        output = self._footnote_mark_re.sub(self._footnote_mark, output)
        self._count = 0
        output = self._footnote_text_re.sub(self._footnote_text, output)
        output = self._footnote_re.sub(self._footnote, output)

        return output, self._footnotes
