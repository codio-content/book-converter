from converter.markdown.paragraph import Paragraph


class TextAsParagraph(object):
    def __init__(self, latex_str, caret_token):
        self.str = latex_str
        self._caret_token = caret_token

    def to_paragraph(self, in_str):
        return Paragraph(in_str).convert().strip()
