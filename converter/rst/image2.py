import re

class Image2(object):
    def __init__(self, source_string, images, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._images = images
        self._image2_re = re.compile(r"""\|(?P<id>\S.*?\S)\|(?= +|$)""")

    def _image2(self, matchobj):
        caret_token = self._caret_token
        image_id = matchobj.group('id')
        image = [image for image in self._images if image.id == image_id]
        if not image:
            return
        image = image[0]
        options = image.options
        alt = options.get('alt', '')

        return f'{caret_token}![{alt}]({image.path}){caret_token}'

    def convert(self):
        output = self._image2_re.sub(self._image2, self.str)
        return output
