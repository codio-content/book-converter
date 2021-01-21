import re


class Math(object):
    def __init__(self, source_string):
        self.str = source_string
        self._math_re = re.compile(r""":math:`(?P<content>.*?)`""")

    @staticmethod
    def _math(matchobj):
        content = matchobj.group('content')
        content = content.replace("\n", " < ")
        content = content.replace("<", " < ")
        content = content.replace("<", " < ")
        content = content.replace(">", " > ")
        content = content.replace("\\+", "+")
        return f'${content}$'

    def convert(self):
        output = self.str
        output = self._math_re.sub(self._math, output)
        return output
