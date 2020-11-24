import re


class Table(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._table_re = re.compile(r"""[+][=]{3,}[+]([=]{3,}[+])+""")
        self._table_row_re = re.compile(r"""\n\s*[|].{3,}[|](.{3,}[|])+""")

    @staticmethod
    def _remove_line_boundaries_by_rst(output):
        output = re.sub(r"\s+[+][-]{3,}[+]([-]{3,}[+])+", "", output)
        return output

    @staticmethod
    def _table(matchobj):
        content = matchobj.group(0).replace('+', '|').replace('=', '-')
        return content

    def _table_row(self, matchobj):
        content = matchobj.group(0)
        content = re.sub(r'( *\|)', '|', self._caret_token + content, 1)
        return content

    def convert(self):
        output = self.str
        output = self._remove_line_boundaries_by_rst(output)
        output = self._table_re.sub(self._table, output)
        output = self._table_row_re.sub(self._table_row, output)
        return output
