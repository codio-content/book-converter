import re
import uuid

from converter.guides.tools import get_text_in_brackets
from converter.markdown.text_as_paragraph import TextAsParagraph


class Tabular(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

        self._graphics_re = re.compile(r"\\includegraphics(\[.*?]){(.*?)}",
                                       flags=re.DOTALL + re.VERBOSE)

        self._table_re = re.compile(r"""\\begin{(?P<block_name>tabular)}
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
        block_contents = block_contents.strip()
        sub_lines = block_contents.split('\n')
        size = get_text_in_brackets(sub_lines[0])
        block_contents = '\n'.join(sub_lines[1:])
        block_contents = block_contents.replace('\\hline', '')
        block_contents = block_contents.replace('\\raggedright', '')
        token = str(uuid.uuid4())

        items = block_contents.split('\\\\')

        table_size = size.strip().strip('|').split('|')

        heading = True
        out = ''
        for row in items:
            row = row.strip()
            if not row:
                continue
            pos = 0
            row = row.replace('\\&', token)

            row = re.sub(r"\\multicolumn{(.*?)}{(.*?)}{(.*?)}", r"\3", row, flags=re.DOTALL + re.VERBOSE)
            row = re.sub(r"\\multirow{(.*?)}{(.*?)}\s?{(.*?)}", r"\3", row, flags=re.DOTALL + re.VERBOSE)

            tabularline_match = re.search(r"\\tabularline", block_contents, flags=re.DOTALL + re.VERBOSE)
            if tabularline_match:
                head = True
                for line in block_contents.split('\n'):
                    line = line.replace('\\\\', '<br/>')
                    line = line.strip()
                    if not line:
                        continue
                    if '\\tabularline' in line and head:
                        out += f'{self._caret_token}|line|{self._caret_token}|-|{self._caret_token}|'
                        head = False
                        continue
                    if '\\tabularline' in line and not head:
                        out += "|" + self._caret_token
                        head = True
                        continue
                    out += line + " "
                out = out.replace('\\tabularline', '')
                break

            t_size = len(table_size)

            match = self._graphics_re.search(row)
            if match:
                row = row.replace('\\icondir', 'icons')
                row = self._graphics_re.sub(r"<img alt='' src='\2' style='width:100px'/>", row)
                t_size = len(row.split("&"))

            for ind in range(0, t_size):
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
