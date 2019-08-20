import re

from collections import namedtuple

from converter.markdown.text_as_paragraph import TextAsParagraph

Code = namedtuple('Code', ['name', 'source'])

code_re = re.compile(r"""\\codefile(\[(?P<guid>.*?)])?{(?P<file_path>.*?)}""",
                     flags=re.DOTALL + re.VERBOSE)


class CodeFile(TextAsParagraph):
    def __init__(self, latex_str, caret_token, percent_token, load_workspace_file):
        super().__init__(latex_str, caret_token)
        self._load_file = load_workspace_file
        self._percent_token = percent_token
        self._source_codes = []

    def make_block(self, matchobj):
        file_path = matchobj.group('file_path')
        file_content = self._load_file(file_path)
        caret_token = self._caret_token

        self._source_codes.append(Code(file_path, file_content))

        file_content = re.sub(r"%", self._percent_token, file_content)
        file_content = re.sub(r"\n", self._caret_token, file_content)

        return f'{caret_token}**source:{file_path}**{caret_token}' \
            f'```code{caret_token}{file_content}{caret_token}```{caret_token}'

    def convert(self):
        output = self.str

        output = code_re.sub(self.make_block, output)

        return output, self._source_codes
