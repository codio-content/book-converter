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
        width = options.get('width', '')
        alt = options.get('alt', '')
        align = options.get('align', '')
        extra_style = 'margin-right: 1em; float: left' if align == 'middle' else ''

        return f'{caret_token}{caret_token}<img src="{image.path}" alt="{alt}" style="width: {width}; ' \
               f'{extra_style}">{caret_token}{caret_token}'

    def convert(self):
        output = self._image2_re.sub(self._image2, self.str)
        return output
