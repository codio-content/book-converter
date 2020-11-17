import re
from collections import namedtuple

Ref = namedtuple('Ref', ['flag', 'ref', 'label'])


class ExternalLink(object):
    def __init__(self, source_string):
        self.str = source_string
        self._externals_links = list()
        self._external_link_re = re.compile(
            r"""\s*\.\. (?P<flag>.*?) raw:: html\n\s*<a\n?\s*href="(?P<link>.*?)".*\n?.*>(?P<label>.*?)</a>""")

    def _external_link(self, matchobj):
        self._externals_links.append(Ref(matchobj.group('flag'),
                                         matchobj.group('link'),
                                         matchobj.group('label')))
        return ""

    def _set_external_links(self, output):
        for link in self._externals_links:
            md_ref = f'[{link.label}]({link.ref})'
            output = output.replace(link.flag, md_ref)
        return output

    def convert(self):
        output = self.str
        output = self._external_link_re.sub(self._external_link, output)
        output = self._set_external_links(output)
        return output
