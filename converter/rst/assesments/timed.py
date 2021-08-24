import re


class Timed(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._assessments = list()
        self._timed_re = re.compile(
            r"""^(?: *\.\.\stimed.*?::(?P<name> .*?)?\n)(?P<settings>\s+:.*?:*\n)?(?P<content>.*?)(?=^\S)""",
            flags=re.MULTILINE + re.DOTALL)

    def _timed(self, matchobj):
        cut_content = []
        content = matchobj.group('content')
        content_list = content.split('\n')
        for ind, item in enumerate(content_list):
            indent_match = re.search(r'^( *)\.\.', content_list[0])
            if indent_match:
                str_len = len(indent_match.group(1))
                cut_content.append(content_list[ind][str_len:])
        return '\n'.join(cut_content)

    def convert(self):
        output = self._timed_re.sub(self._timed, self.str)
        return output
