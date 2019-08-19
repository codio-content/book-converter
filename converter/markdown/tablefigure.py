import re
import uuid

from converter.markdown.text_as_paragraph import TextAsParagraph

table_re = re.compile(r"""\\tablefigure{(?P<file_path>.*?)}{(?P<label>.*?)}""",
                      flags=re.DOTALL + re.VERBOSE)


class TableFigure(TextAsParagraph):
    def __init__(self, latex_str, caret_token, load_workspace_file):
        super().__init__(latex_str, caret_token)
        self._load_file = load_workspace_file
        self._matches = []

    def make_block(self, matchobj):
        file_path = matchobj.group('file_path')
        file_content = self._load_file(file_path)
        caret_token = self._caret_token
        replace_token = str(uuid.uuid4())

        self._matches.append(replace_token)

        return f'{file_content}{caret_token}{caret_token}{replace_token}'

    def remove_matched_token(self, output, chars):
        pos = output.find(chars)
        token_len = len(chars) + 1
        if pos == -1:
            return output
        level = 0
        for index in range(pos + token_len, len(output), 1):
            ch = output[index]
            if ch == '}':
                if level == 0:
                    output = output[0:pos] + output[pos + token_len:index - 1] + output[index + 1:]
                    break
                else:
                    level += 1
            elif ch == '{':
                level -= 1
        return output

    def convert(self):
        output = self.str

        output = table_re.sub(self.make_block, output)

        for token in self._matches:
            output = self.remove_matched_token(output, token)

        return output
