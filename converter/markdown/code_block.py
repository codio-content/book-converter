import re

from collections import namedtuple

Code = namedtuple('Code', ['name', 'source'])


class CodeBlock(object):
    def __init__(self, latex_str, percent_token, caret_token, remove_trinket):
        self.str = latex_str
        self.token = percent_token
        self._caret_token = caret_token
        self._source_codes = []
        self._remove_trinket = remove_trinket

        self._code_re = re.compile(r"""\\begin{(?P<block_name>code|stdout|verbatim)}
                                    (?P<block_contents>.*?)
                                    \\end{(?P=block_name)}""",
                                   flags=re.DOTALL + re.VERBOSE)

        self._trinket_re = re.compile(r"""\\begin{(?P<block_name>trinket)}[\[\]0-9]*{(?P<file_name>.*?)}
                                    (?P<block_contents>.*?)
                                    \\end{(?P=block_name)}""",
                                      flags=re.DOTALL + re.VERBOSE)

    def _code_block(self, matchobj):
        caret_token = self._caret_token
        block_contents = matchobj.group('block_contents')
        try:
            file_name = matchobj.group('file_name')
            self._source_codes.append(Code(file_name, block_contents))
        except IndexError:
            pass
        block_name = matchobj.group('block_name')
        if self._remove_trinket and block_name == 'trinket':
            return ''
        block_contents = re.sub(r'%', self.token, block_contents)
        block_contents = re.sub(r'\n', self._caret_token, block_contents)
        return f'{caret_token}```code{block_contents}```{caret_token}'

    def convert(self):
        output = self.str
        output = self._code_re.sub(self._code_block, output)
        output = self._trinket_re.sub(self._code_block, output)
        return output, self._source_codes
