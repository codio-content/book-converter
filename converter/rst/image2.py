import re


class Image2(object):
    def __init__(self, source_string, tags, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._tags = tags
        self._image2_re = re.compile(r"""\|(?P<tag>\S.*?\S)\|(?= +|$)""")

    def _image2(self, matchobj):
        caret_token = self._caret_token
        tag = matchobj.group('tag')
        image = [item for item in self._tags if item.type == 'image' and item.tag == tag]
        if not image:
            return
        image = image[0]
        options = image.options
        width = options.get('width', '')
        alt = options.get('alt', '')
        align = options.get('align', '')
        extra_style = 'margin-right: 1em; float: left' if align == 'middle' else ''

        return f'{caret_token}{caret_token}<img src="{image.data}" alt="{alt}" style="width: {width}; ' \
               f'{extra_style}">{caret_token}{caret_token}\n'

    def convert(self):
        output = self._image2_re.sub(self._image2, self.str)
        return output
