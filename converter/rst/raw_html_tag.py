import re


class RawHtmlTag(object):
    def __init__(self, source_string, tags, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._tags = tags
        self._raw_html_tag_re = re.compile(r""" ?\|(?P<tag>.*?)\| ?""")

    def _raw_html_tag(self, matchobj):
        tag = matchobj.group('tag')
        raw_html_data = [item for item in self._tags if item.type == 'html_link' and item.tag == tag]
        if not raw_html_data:
            return matchobj.group(0)
        content = raw_html_data[0].data
        return f' {content} '

    def convert(self):
        output = self._raw_html_tag_re.sub(self._raw_html_tag, self.str)
        return output
