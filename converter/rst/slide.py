import re


class Slide(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._slide_re = re.compile(r"""^\.\. slide:: +.*?\n(?P<settings>\s+:.*?:*\n)?(?P<content>.*?)\n(?=\S)""",
                                    flags=re.MULTILINE + re.DOTALL)

    def _slide(self, matchobj):
        cut_content = []
        content = matchobj.group('content').lstrip('\n').rstrip()
        content_list = content.split('\n')
        for ind, item in enumerate(content_list):
            indent_match = re.search(r'^( *)\.\.', content_list[0])
            if indent_match:
                str_len = len(indent_match.group(1))
                cut_content.append(content_list[ind][str_len:])
        return '\n'.join(cut_content) + '\n\n'

    def convert(self):
        output = self._slide_re.sub(self._slide, self.str)
        return output
