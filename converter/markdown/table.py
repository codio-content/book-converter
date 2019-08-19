import re


class Table(object):
    def __init__(self, latex_str, caret_token):
        self.str = latex_str
        self._caret_token = caret_token

        self._table_re = re.compile(r"""\\begin{(?P<block_name>table|tabular)} # block name
                                    (?P<block_contents>.*?) # Non-greedy block contents
                                    \\end{(?P=block_name)}""",  # closing block
                                    flags=re.DOTALL + re.VERBOSE)

    def _format_table(self, matchobj):
        block_contents = matchobj.group('block_contents')

        out_str = ""
        caption = ""
        table = []

        for line in block_contents.strip().split("\n"):
            line = line.rstrip("\\")
            if line == "\\hline":
                out_str += self._caret_token
                continue
            elif line.startswith("\\end") or line.startswith("\\begin") or line.startswith("[!ht]") or '&' not in line:
                continue
            elif line.startswith("\\caption"):
                caption = line[9:-1]
                continue
            out_str += line
            table.append(line.split(' & '))

        heading = True
        out = ""

        if caption:
            out += "**Table: " + caption + "**" + self._caret_token

        for row in table:
            pos = 0
            for col in row:
                out += "|" + col.replace('|', '&#124;')
            if heading:
                out += '|' + self._caret_token
                for _ in row:
                    out += "|-"
                    pos += 1
            heading = False
            out += '|' + self._caret_token

        return out

    def convert(self):
        output = self.str
        output = self._table_re.sub(self._format_table, output)

        return output
