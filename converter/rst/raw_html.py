import re
from collections import namedtuple

RawHtmlData = namedtuple('RawHtmlData', ['marker', 'content'])


class RawHtml(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._links = list()
        self._raw_html_re = re.compile(
            r"""^[ ]*(?P<indent>^[ ]+-[ ]+)?\.\.[ ]+(?:\|(?P<marker>[\w+\s]+)\|[ ]+)?raw::[ ]html\n.*?\n
            (?P<content>\s*.*?)\n(?=\S|^[ ]*$)""", flags=re.MULTILINE + re.DOTALL + re.VERBOSE)

    def _raw_html(self, matchobj):
        marker = matchobj.group('marker')
        indent = matchobj.group('indent')
        content = matchobj.group('content').strip()
        if marker:
            marker = marker.strip()
            self._links.append(RawHtmlData(marker, content))
            return ''
        else:
            split_content = [f' {item.lstrip()}' for item in content.split('\n')]
            final_content = '\n'.join(split_content)
            indent = indent or ''
            return f' {indent}{final_content}'

    def convert(self):
        output = self._raw_html_re.sub(self._raw_html, self.str)
        return output, self._links
