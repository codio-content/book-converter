import re


class Footnote(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._footnote_counter = 0
        self._marker_footnote_re = re.compile(r"""\[#]_""")
        self._bib_footnote_re = re.compile(r"""\[(.*?)]_""")
        self._footnote_re = re.compile(r"""(^\.\. \[#] )(?P<content>.*?\n)(?=^$|\1|(?![^$]+$))""", flags=re.MULTILINE)

    def _bib_foot_note(self, matchobj):
        return f'<span style="color: #0c3762;">**[{matchobj.group(1)}]**</span>'

    def _foot_note_marker(self, matchobj):
        self._footnote_counter += 1
        return f'<span style="color: #0c3762;">**[{self._footnote_counter}]**</span>'

    def _foot_note(self, matchobj):
        self._footnote_counter += 1
        content = matchobj.group('content')
        out = []
        for line in content.split('\n'):
            out.append(line)
        content = ' '.join(out)
        return f'<span style="color: #0c3762;">**[{self._footnote_counter}]**</span> {content}' \
               f'{self._caret_token}{self._caret_token}'

    def convert(self):
        output = self.str
        output = self._marker_footnote_re.sub(self._foot_note_marker, output)
        self._footnote_counter = 0
        output = self._footnote_re.sub(self._foot_note, output)
        output = self._bib_footnote_re.sub(self._bib_foot_note, output)
        return output
