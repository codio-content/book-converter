import re
from collections import namedtuple

Ref = namedtuple('Ref', ['flag', 'ref', 'label'])


class ExternalLink(object):
    def __init__(self, source_string):
        self.str = source_string
        self._externals_links = list()
        self._external_link_re = re.compile(r"""`(?P<name>.*?)\n?<(?P<ref>https?:.*?)>`_""")
        self._external_link_by_tag_re = re.compile(
            r"""\s*\.\. (?P<flag>.*?) raw:: html\n\s*<a\n?\s*href="(?P<link>.*?)".*\n?.*>(?P<label>.*?)</a>""")

    def _external_link_by_tag(self, matchobj):
        self._externals_links.append(Ref(matchobj.group('flag'),
                                         matchobj.group('link'),
                                         matchobj.group('label')))
        return ""

    @staticmethod
    def _external_link(matchobj):
        name = matchobj.group('name')
        ref = matchobj.group('ref')
        name = name.strip()
        return f'[{name}]({ref})'

    def _set_external_links_by_tag(self, output):
        for link in self._externals_links:
            md_ref = f'[{link.label}]({link.ref})'
            output = output.replace(link.flag, md_ref)
        return output

    def convert(self):
        output = self.str
        output = self._external_link_re.sub(self._external_link, output)
        output = self._external_link_by_tag_re.sub(self._external_link_by_tag, output)
        output = self._set_external_links_by_tag(output)
        return output
