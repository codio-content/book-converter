import re


class Character(object):
    def __init__(self, source_string):
        self.str = source_string
        self._character_re = re.compile(r"""\\\\\$(?=\d)""")

    @staticmethod
    def _character(matchobj):
        return "<span style='font-size: 80%;'>$</span>"

    def convert(self):
        output = self.str
        output = self._character_re.sub(self._character, output)
        return output
