import re

TAB_SIZE = 4


class List(object):
    def __init__(self, source_string):
        self.str = source_string
        self._list_re = re.compile(r"""\n(?P<tabs>[\t]+)(?P<marker>[-|]?)?""")
        self._indented_list_re = re.compile(r"""^ {4,}(\d\.|#\.|\*|-)\s.*?\n""", flags=re.MULTILINE)
        self._lists_re = re.compile(r"""^(\d\.|#\.|\*|-)[ ]+(.*?\n.*?)\n(?=\S|(?![^$]+$))""",
                                    flags=re.MULTILINE + re.DOTALL)

    @staticmethod
    def _list(matchobj):
        tabs = matchobj.group('tabs')
        marker = matchobj.group('marker')
        indent_size = 0
        if tabs:
            indent_size = len(tabs)
        if marker and marker == "|":
            indent_size += 1
        if indent_size >= 1:
            indent_size = indent_size - 1
        content = '* '
        content = ' ' * indent_size * TAB_SIZE + content
        return '\n' + content

    @staticmethod
    def _indented_list(matchobj):
        content = matchobj.group(0)
        strip_content = [f'{item[2:]}\n' for item in content.split('\n') if item.strip()]
        return '\n'.join(strip_content)

    @staticmethod
    def _lists_align(matchobj):
        content = matchobj.group(0)
        content = content.replace('\n', ' ')
        content = re.sub(r'[ ]{2,}', ' ', content)
        return f'{content}\n\n'

    def convert(self):
        output = self.str
        output = self._list_re.sub(self._list, output)
        output = self._indented_list_re.sub(self._indented_list, output)
        output = self._lists_re.sub(self._lists_align, output)
        return output
