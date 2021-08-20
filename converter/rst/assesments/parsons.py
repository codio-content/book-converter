import re


class Parsons(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._parsonsprob_re = re.compile(r"""^( *\.\.\sparsonsprob:: ?(?P<name>.*?)?\n)(?P<options>.*?)\n(?=\S)""",
                                          flags=re.MULTILINE + re.DOTALL)

    def _parsonsprob(self, matchobj):

        return '<<<<<< PARSONS ASSESSMENT >>>>>>>\n'

    def convert(self):
        output = self._parsonsprob_re.sub(self._parsonsprob, self.str)
        return output, self._assessments
