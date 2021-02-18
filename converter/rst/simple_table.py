import re


class SimpleTable(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._simple_table_re = re.compile(
            r"""([ ]*[=]{3,}([ ]{2,}[=]{3,})+)\n(?P<headers>.*?)\n([ ]*[=]{3,}([ ]{2,}[=]{3,})+)\n
                (?P<rows>(.*?[ ]{2,}.*?\n)+)([ ]*[=]{3,}([ ]{2,}[=]{3,})+)""", flags=re.VERBOSE)

    def _simple_table(self, matchobj):
        headers = self._get_row(matchobj.group('headers'))
        line_boundarie = self._get_line_boundarie(headers)
        rows = ''
        raw_rows = matchobj.group('rows').split('\n')
        for raw_row in raw_rows:
            row = self._get_row(raw_row)
            rows = rows + row
        return f'{headers}{line_boundarie}{rows}'

    def _get_row(self, raw_row: str):
        row = raw_row.strip()
        return re.sub(r'\s{2,}', '|', row) + self._caret_token

    def _get_line_boundarie(self, headers):
        return re.sub(r'[^|]', '-', headers) + self._caret_token

    def convert(self):
        output = self.str
        output = self._simple_table_re.sub(self._simple_table, output)
        return output
