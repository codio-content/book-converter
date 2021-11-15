import re


class NestedContent(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._timed_re = re.compile(
            r"""^\.\.[ ]+(timed|reveal)::[ ]+(?P<name>[^\n]+)\n((?: +:[^\n]+\n)+)?(?P<content>.*?)\n(?=\S|(?!^$)$)""",
            flags=re.MULTILINE + re.DOTALL)

    def _timed(self, matchobj):
        cut_content = []
        content = matchobj.group('content').lstrip('\n').rstrip()
        content_list = content.split('\n')
        for ind, item in enumerate(content_list):
            if re.search(r'^[ ]{3}', item):
                item = item[3:]
            cut_content.append(item)
        return '\n'.join(cut_content) + '\n\n'

    def convert(self):
        output = self._timed_re.sub(self._timed, self.str)
        return output
