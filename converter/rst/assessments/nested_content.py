import re


class NestedContent(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._timed_re = re.compile(
            r"""^\.\.[ ]+(timed|reveal)::[ ]+(?P<name>[^\n]+)\n((?:(?P<indent>[ ]+):[^\n]+\n)+)?
            (?P<content>.*?)\n(?=\S|(?!^$)$)""", flags=re.MULTILINE + re.DOTALL + re.VERBOSE)

    def _timed(self, matchobj):
        cut_content = []
        content = matchobj.group('content').lstrip('\n').rstrip()
        indent = len(matchobj.group('indent')) if matchobj.group('indent') else 3
        content_list = content.split('\n')
        for ind, item in enumerate(content_list):
            if re.search(fr'^[ ]{{{indent}}}', item):
                item = item[indent:]
            cut_content.append(item)
        return '\n'.join(cut_content) + '\n\n'

    def convert(self):
        output = self._timed_re.sub(self._timed, self.str)
        return output
