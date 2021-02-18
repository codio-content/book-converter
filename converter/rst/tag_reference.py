import re


class TagReference(object):
    def __init__(self, source_string, tags):
        self.str = source_string
        self._tags = tags
        self._tag_reference_re = re.compile(r""":num:`[a-zA-Z0-9]*[ ]?#(?P<tag>[a-zA-Z0-9]*)`""")

    def _tag_reference(self, matchobj):
        figure_number = ''
        tag = matchobj.group('tag') if matchobj.group('tag') is not None else False
        if tag and tag in self._tags:
            figure_number = self._tags[tag]
        return f'{figure_number}'

    def convert(self):
        output = self.str
        output = self._tag_reference_re.sub(self._tag_reference, output)
        return output
