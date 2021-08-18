import re
from collections import namedtuple

Image2data = namedtuple('Image2data', ['id', 'path', 'options'])


class Image2Directives(object):
    def __init__(self, source_string):
        self.str = source_string
        self._images = list()
        self._image2directives_re = re.compile(
            r"""^ *\.\.\s+\|(?P<id>.*?)\|\s+image:: ?(?P<path>.*?)?\n(?P<opt>.*?)\n(?=\S)""",
            flags=re.MULTILINE + re.DOTALL)

    def _image2directives(self, matchobj):
        options = {}
        image_id = matchobj.group('id')
        path = matchobj.group('path')
        options_group = matchobj.group('opt').split('\n')
        option_re = re.compile(':([^:]+): (.+)')
        for line in options_group:
            opt_match = option_re.match(line.strip())
            if opt_match:
                options[opt_match[1]] = opt_match[2]
        self._images.append(Image2data(image_id, path, options))

        return ''

    def convert(self):
        output = self._image2directives_re.sub(self._image2directives, self.str)
        return output, self._images
