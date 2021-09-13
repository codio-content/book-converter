import re


class ExternalLink(object):
    def __init__(self, source_string):
        self.str = source_string
        self._externals_links = list()
        self._external_link_re = re.compile(r"""`(?P<name>.*?)\n?<(?P<ref>https?:.*?)>`_""")

    @staticmethod
    def _external_link(matchobj):
        name = matchobj.group('name')
        ref = matchobj.group('ref')
        name = name.strip()
        return f'[{name}]({ref})'

    def convert(self):
        output = self.str
        output = self._external_link_re.sub(self._external_link, output)
        return output
