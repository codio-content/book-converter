import re
import uuid


class Paragraph(object):
    def __init__(self, latex_str):
        self.str = latex_str

        self._local_caret_token = str(uuid.uuid4())

    def convert_without_tags(self):
        level = 0
        processed = []
        local_lines = []

        output = self.str
        empty_lines_count = 0

        for line in output.split('\n'):
            if not line:
                empty_lines_count += 1
            else:
                empty_lines_count = 0
            if '\\begin' in line:
                level += 1
                if local_lines:
                    processed.append(' '.join(local_lines))
                    local_lines = []
                processed.append(line)
            elif '\\end' in line:
                processed.append(line)
                level -= 1
            else:
                if empty_lines_count > 0:
                    if local_lines:
                        processed.append(' '.join(local_lines))
                        local_lines = []
                    processed.append('')
                    empty_lines_count = 0
                elif level > 0:
                    processed.append(line)
                elif line:
                    local_lines.append(line.lstrip())

        if local_lines:
            processed.append(' '.join(local_lines))

        output = '\n'.join(processed)
        return output

    def convert(self):
        output = self.str

        output = re.sub(r"[\n]{2,}", self._local_caret_token, output)
        output = re.sub(r"\n", ' ', output)
        output = re.sub(self._local_caret_token, '\n', output)

        return output
