from converter.markdown.match_elements import match_elements
from converter.markdown.text_as_paragraph import TextAsParagraph


class Quotation(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def convert(self):
        out = self.str
        search_str = "\\makequotation"
        pos = out.find(search_str)
        caret_token = self._caret_token
        while pos != -1:
            matches, index = match_elements(out[pos + len(search_str):], 2)
            start = out[0:pos]
            end_pos = pos + len(search_str) + 1 + index
            end = out[end_pos:]
            out = start + f'{caret_token}> {matches[0]}{caret_token}>' \
                          f'{caret_token}> __{matches[1]}__{caret_token}{caret_token}' + end
            pos = out.find(search_str, end_pos + 1)
        return out
