import re

from converter.markdown.text_as_paragraph import TextAsParagraph

dedication_re = re.compile(
    r"""\\dedicationwithpic(\[(?P<settings>.*?)]){(?P<image>.*?)}{(?P<block_contents>.*?)}""",
    flags=re.DOTALL + re.VERBOSE
)


class DedicationWithPic(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)
        self.images = []

    def make_block(self, matchobj):
        content = self.to_paragraph(matchobj.group('block_contents'))
        image = matchobj.group('image').strip()
        if image.lower().endswith('.pdf'):
            self.images.append(image)
            image = image.replace('.pdf', '.jpg')
        caret_token = self._caret_token
        return f"![{content}]({image}){caret_token}{caret_token}{content}{caret_token}"

    def convert(self):
        return dedication_re.sub(self.make_block, self.str), self.images
