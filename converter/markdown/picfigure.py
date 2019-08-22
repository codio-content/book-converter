import re

picfigure_re = re.compile(r"""\\picfigure{(?P<image>.*?)}{(?P<refs>.*?)}{(?P<content>.*?)}""",
                          flags=re.DOTALL + re.VERBOSE)


class PicFigure(object):
    def __init__(self, latex_str, detect_asset_ext):
        self.str = latex_str
        self.images = []
        self._detect_asset_ext = detect_asset_ext

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
        return "![{}]({})  \n{}".format(content, image, content)

    def convert(self):
        self.images.clear()
        pdfs = filter(lambda img: img.endswith('.pdf'), self.images)
        return picfigure_re.sub(self.make_block, self.str), list(pdfs)
