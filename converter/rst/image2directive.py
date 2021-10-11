import re

from converter.rst.model.tag_directives import TagDirectives


class Image2Directives(object):
    def __init__(self, source_string):
        self.str = source_string
        self._images = list()
        self._image2directives_re = re.compile(
            r"""^ *\.\.\s+\|(?P<id>[^\n]+)\|\s+image:: ?(?P<path>[^\n]+)?\n(?P<opt>.*?)\n(?=\S|(?!^$)$)""",
            flags=re.MULTILINE + re.DOTALL)

    def _image2directives(self, matchobj):
        options = {}
        image_id = matchobj.group('id')
        path = matchobj.group('path')
        options_group = matchobj.group('opt')
        option_re = re.compile(':([^:]+): (.+)')
        for line in options_group.split('\n'):
            opt_match = option_re.match(line.strip())
            if opt_match:
                options[opt_match[1]] = opt_match[2]
        self._images.append(TagDirectives(image_id, 'image', path, options))

        return ''

    def convert(self):
        output = self._image2directives_re.sub(self._image2directives, self.str)
        return output, self._images
