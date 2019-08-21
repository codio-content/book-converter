import re

from converter.markdown.tabular import Tabular


class Tabularx(Tabular):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

        self._table_re = re.compile(r"""\\begin{(?P<block_name>tabularx)}{(?P<settings>.*?)}{(?P<size>.*?)}
                                    (?P<block_contents>.*?)
                                    \\end{(?P=block_name)}""",
                                    flags=re.DOTALL + re.VERBOSE)
