import re


class ActiveCode(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._activecode_re = re.compile(r"""^( *\.\.\sactivecode:: ?(?P<name>.*?)?\n)(?P<options>.*?)\n(?=\S)""",
                                         flags=re.MULTILINE + re.DOTALL)

    def _activecode(self, matchobj):

        return ''

    def convert(self):
        output = self._activecode_re.sub(self._activecode, self.str)
        return output, self._assessments
