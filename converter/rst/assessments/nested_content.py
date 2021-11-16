import re


class NestedContent(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._nested_content_re = re.compile(
            r"""^\.\.[ ]+(timed|reveal)::[ ]+(?P<name>[^\n]+)\n((?:(?P<indent>[ ]+):[^\n]+\n)+)?
            (?P<content>.*?)\n(?=\S|(?!^$)$)""", flags=re.MULTILINE + re.DOTALL + re.VERBOSE)

    def _nested_content(self, matchobj):
        cut_content = []
        content = matchobj.group('content').lstrip('\n').rstrip()
        indent_matched = False
        indent = 0
        for ind, item in enumerate(content.split('\n')):
            if not indent_matched:
                match_indent = re.search(fr'^([ ]+)\S', item)
                if match_indent:
                    indent = len(match_indent.group(1))
                    indent_matched = True
            cut_content.append(item[indent:])
        return '\n'.join(cut_content) + '\n\n'

    def convert(self):
        output = self._nested_content_re.sub(self._nested_content, self.str)
        return output
