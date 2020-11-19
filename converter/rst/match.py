import re


class Match(object):
    def __init__(self, source_string):
        self.str = source_string
        self._math_re = re.compile(r""":math:`(?P<content>.*?)`""")
        self._math_block_re = re.compile(r""" {,3}.. math::\n^[\s\S]*?(?P<content>.*?)(?=\n{2,})""",
                                         flags=re.MULTILINE + re.DOTALL)

    @staticmethod
    def _math(matchobj):
        content = matchobj.group('content')
        content = content.replace("\\+", "+")
        return f'$${content}$$'

    @staticmethod
    def _math_block(matchobj):
        content = matchobj.group('content')
        content = content.strip()
        content = content.replace("\\+", "+")
        content = content.replace("&=&", "\\&=\\&")
        return f'<center style="font-size: 80%;">$${content}$$</center>'

    def convert(self):
        output = self.str
        output = self._math_re.sub(self._math, output)
        output = self._math_block_re.sub(self._math_block, output)
        return output
