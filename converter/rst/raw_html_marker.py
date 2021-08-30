import re


class RawHtmlMarker(object):
    def __init__(self, source_string, links, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._links = links
        self._raw_html_marker_re = re.compile(r""" ?\|(?P<id>.*?)\| ?""")

    def _raw_html_marker(self, matchobj):
        marker_id = matchobj.group('id')
        raw_html_data = [image for image in self._links if image.id == marker_id]
        content = raw_html_data[0].content if raw_html_data else marker_id
        return f' {content} '

    def convert(self):
        output = self._raw_html_marker_re.sub(self._raw_html_marker, self.str)
        return output
