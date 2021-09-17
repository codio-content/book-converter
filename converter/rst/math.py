import re


class Math(object):
    def __init__(self, source_string):
        self.str = source_string
        self._math_re = re.compile(r""":math:`(?P<content>.*?)`""")
        self._sup_re = re.compile(r"""([\S\d]+)\\ :sup:`(.*?)`""")

    @staticmethod
    def _math(matchobj):
        content = matchobj.group('content')
        content = content.replace("\n", " < ")
        content = content.replace("<", " < ")
        content = content.replace("<", " < ")
        content = content.replace(">", " > ")
        content = content.replace("\\+", "+")
        return f'${content}$'

    @staticmethod
    def _sup(matchobj):
        return f'${matchobj.group(1)}^{{{matchobj.group(2)}}}$'

    def convert(self):
        output = self.str
        output = self._math_re.sub(self._math, output)
        output = self._sup_re.sub(self._sup, output)
        return output
