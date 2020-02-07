from converter.markdown.text_as_paragraph import TextAsParagraph


class Quotation(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def match_elements(self, text, n_matches):
        level = 0
        offset = 0
        found_matches = 0
        founds = []
        last_index = 0
        for index in range(0, len(text), 1):
            ch = text[index]
            last_index = index
            if ch == '}':
                level -= 1
                if level == 0:
                    start_position = text.find("{", offset) + 1
                    offset += start_position
                    founds.append(text[start_position:index])
                    found_matches += 1
                    if found_matches == n_matches:
                        break
            elif ch == '{':
                level += 1
        return founds, last_index

    def convert(self):
        out = self.str
        search_str = "\\makequotation"
        pos = out.find(search_str)
        caret_token = self._caret_token
        while pos != -1:
            matches, index = self.match_elements(out[pos + len(search_str):], 2)
            start = out[0:pos]
            end_pos = pos + len(search_str) + 1 + index
            end = out[end_pos:]
            out = start + f'{caret_token}> {matches[0]}{caret_token}>' \
                f'{caret_token}> __{matches[1]}__{caret_token}{caret_token}' + end
            pos = out.find(search_str, end_pos + 1)
        return out
