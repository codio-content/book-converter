import re


class Table(object):
    def __init__(self, latex_str, caret_token):
        self.str = latex_str
        self._caret_token = caret_token

        self._table_re = re.compile(r"""\\begin{(?P<block_name>table)}(\[.*])? # block name
                                    (?P<block_contents>.*?) # Non-greedy block contents
                                    \\end{(?P=block_name)}""",  # closing block
                                    flags=re.DOTALL + re.VERBOSE)

    def _format_table(self, matchobj):
        block_contents = matchobj.group('block_contents')

        out_str = ""
        caption = ""

        table_lines = []

        for line in block_contents.strip().split("\n"):
            if line.startswith("\\caption"):
                caption = line[9:-1]
            else:
                table_lines.append(line)

        if caption:
            out_str += "**Table: " + caption + "**"

        table_content = '\n'.join(table_lines)

        caret_token = self._caret_token

        return f'{caret_token}{table_content}{caret_token}{out_str}{caret_token}'

    def convert(self):
        output = self.str
        output = self._table_re.sub(self._format_table, output)

        return output
