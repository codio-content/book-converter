import re


class RawHtmlMarker(object):
    def __init__(self, source_string, links, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._links = links
        self._raw_html_marker_re = re.compile(r""" ?\|(?P<marker>.*?)\| ?""")

    def _raw_html_marker(self, matchobj):
        marker = matchobj.group('marker')
        raw_html_data = [link for link in self._links if link.marker == marker]
        if not raw_html_data:
            return matchobj.group(0)
        content = raw_html_data[0].content
        return f' {content} '

    def convert(self):
        output = self._raw_html_marker_re.sub(self._raw_html_marker, self.str)
        return output
