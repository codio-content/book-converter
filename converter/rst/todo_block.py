import re


class TodoBlock(object):
    def __init__(self, source_string):
        self.str = source_string
        self._todo_block_re = re.compile(
            r"""\.\. [a-zA-Z]+::\n +:type: (?P<type>[a-zA-Z]+)\n*(?P<content>(?:\s+[^\n]+\n*)*)""", flags=re.MULTILINE
        )

    @staticmethod
    def _todo_block(matchobj):
        return ''

    def convert(self):
        output = self.str
        output = self._todo_block_re.sub(self._todo_block, output)
        return output
