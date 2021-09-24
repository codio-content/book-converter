import re

from converter.rst.model.tag_directives import TagDirectives


class RawHtmlDirectives(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._links = list()
        self._raw_html_re = re.compile(
            r"""^(?P<indent>[ ]*)(?P<dash>^[ ]+-[ ]+)?\.\.[ ]+(?:\|(?P<tag>[\w+\s]+)\|[ ]+)?
            raw::[ ]html\n.*?\n(?P<content>\s*.*?)\n(?=\S|^[ ]*$)""", flags=re.MULTILINE + re.DOTALL + re.VERBOSE)

    def _raw_html(self, matchobj):
        tag = matchobj.group('tag')
        indent = matchobj.group('indent')
        dash_indent = matchobj.group('dash')
        content = matchobj.group('content').strip()
        if tag:
            tag = tag.strip()
            self._links.append(TagDirectives(tag, 'html_link', content, {}))
            return ''
        else:
            split_content = [f' {item.lstrip()}' for item in content.split('\n')]
            final_content = '\n'.join(split_content)
            if not indent and not dash_indent:
                return final_content
            dash_indent = dash_indent or ''
            return f'{dash_indent}{final_content}'

    def convert(self):
        output = self._raw_html_re.sub(self._raw_html, self.str)
        return output, self._links
