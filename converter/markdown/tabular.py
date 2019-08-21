import re
import uuid

from converter.markdown.text_as_paragraph import TextAsParagraph


class Tabular(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

        self._table_re = re.compile(r"""\\begin{(?P<block_name>tabular)}{(?P<size>.*?)}
                                    (?P<block_contents>.*?)
                                    \\end{(?P=block_name)}""",
                                    flags=re.DOTALL + re.VERBOSE)

    def safe_list_get(self, list, idx, default):
        try:
            return list[idx]
        except IndexError:
            return default

    def _format_table(self, matchobj):
        block_contents = matchobj.group('block_contents')
        size = matchobj.group('size')
        block_contents = block_contents.strip()
        token = str(uuid.uuid4())

        items = block_contents.split('\\hline')

        table_size = size.strip().strip('|').split('|')

        heading = True
        out = ''
        for row in items:
            if not row:
                continue
            pos = 0
            row = row.replace('\\&', token)
            for ind in range(0, len(table_size)):
                data = row.split('&')
                col = self.safe_list_get(data, ind, '').strip()
                col = col.replace('\n', '<br/>')
                col = col.replace('\\\\', '')
                out += "|" + col.replace('|', '&#124;')
            if heading:
                out += '|' + self._caret_token
                for _ in range(0, len(table_size)):
                    out += "|-"
                    pos += 1
            heading = False
            out += '|' + self._caret_token

        out = out.replace(token, '\\&')

        return out

    def convert(self):
        output = self.str
        output = self._table_re.sub(self._format_table, output)

        return output
