import re


class Ignore(object):
    def __init__(self, source_string):
        self.str = source_string
        self._ignore_re = re.compile(r"""^\.\.\s+(?:(index|toctree|qnum|highlight)::|controversial)\n.*?\n(?=\S)""",
                                     flags=re.MULTILINE + re.DOTALL)
        self._data_file_re = re.compile(r"""^( *\.\.\sdatafile:: (?P<name>.*?)\n)(?P<options>.*?)\n(?=\S|(?!^$)$)""",
                                        flags=re.MULTILINE + re.DOTALL)

    def _ignore(self, matchobj):
        return ''

    def _data_file(self, matchobj):
        filename = matchobj.group('name')
        return f'**Data file: {filename}**\n\n'

    def convert(self):
        output = self.str
        output = self._ignore_re .sub(self._ignore, output)
        output = self._data_file_re.sub(self._data_file, output)
        return output
