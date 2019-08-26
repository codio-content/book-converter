import re

from converter.markdown.text_as_paragraph import TextAsParagraph

picfigure_re = re.compile(r"""\\picfigure{(?P<image>.*?)}{(?P<refs>.*?)}{(?P<content>.*?)}""",
                          flags=re.DOTALL + re.VERBOSE)


class PicFigure(TextAsParagraph):
    def __init__(self, latex_str, caret_token, detect_asset_ext, figure_counter_offset, chapter_num):
        super().__init__(latex_str, caret_token)
        self.images = []
        self._detect_asset_ext = detect_asset_ext
        self._figure_counter = 0
        self._figure_counter_offset = figure_counter_offset
        self._chapter_num = chapter_num

    def make_block(self, matchobj):
        content = matchobj.group('content').strip()
        image = matchobj.group('image').strip()
        if '.' not in image:
            ext = self._detect_asset_ext(image)
            if ext:
                image = '{}.{}'.format(image, ext)
        if image.lower().endswith('.pdf'):
            self.images.append(image)
            image = image.replace('.pdf', '.jpg')
        self._figure_counter += 1
        caption = '**Figure {}.{}**'.format(
            self._chapter_num, self._figure_counter + self._figure_counter_offset
        )
        caret_token = self._caret_token
        return f"![{content}]({image}){caret_token}{caption}{caret_token}{content}"

    def convert(self):
        self.images.clear()
        pdfs = filter(lambda img: img.endswith('.pdf'), self.images)
        return picfigure_re.sub(self.make_block, self.str), list(pdfs), self._figure_counter
