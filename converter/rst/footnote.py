import re


class Footnote(object):
    def __init__(self, source_string):
        self.str = source_string
        self._footnote_counter = 0
        self._marker_footnote_re = re.compile(r"""\[#]_""")
        self._footnote_re = re.compile(r"""\.\. \[#]""")

    def _foot_note(self, matchobj):
        self._footnote_counter += 1
        return f'[{self._footnote_counter}]'

    def convert(self):
        output = self.str
        output = self._marker_footnote_re.sub(self._foot_note, output)
        self._footnote_counter = 0
        output = self._footnote_re.sub(self._foot_note, output)
        return output
