import re


class Rst2Markdown(object):
    def __init__(self, lines_array, chapter_num=1):
        self._chapter_num = chapter_num
        self.lines_array = lines_array
        self._heading1_re = re.compile(r"""^(?P<content>.*?\n)?(?:=)+\s*$""", flags=re.MULTILINE)
        self._heading2_re = re.compile(r"""^(?P<content>.*?\n)?(?:-)+\s*$""", flags=re.MULTILINE)
        self._heading3_re = re.compile(r"""^(?P<content>.*?\n)?(?:~)+\s*$""", flags=re.MULTILINE)
        self._heading4_re = re.compile(r"""^(?P<content>.*?\n)?(?:")+\s*$""", flags=re.MULTILINE)
        self._list_re = re.compile(r"""^#\.(?P<content>.*?)\s*?$""", flags=re.MULTILINE)
        self._specific_re = re.compile(r"""""", flags=re.MULTILINE)

    def _heading1(self, matchobj):
        content = matchobj.group('content')
        return f'# {content}'

    def _heading2(self, matchobj):
        content = matchobj.group('content')
        return f'## {content}'

    def _heading3(self, matchobj):
        content = matchobj.group('content')
        return f'### {content}'

    def _heading4(self, matchobj):
        content = matchobj.group('content')
        return f'#### {content}'

    def _list(self, matchobj):
        content = matchobj.group('content')
        content = content.strip()
        return f'1. {content}'

    def _rst_specific(self, matchobj):
        content = matchobj.group('content')
        content = content.strip()
        return f'1. {content}'

    def to_markdown(self):
        output = '\n'.join(self.lines_array)
        # output = self._specific_re.sub(self._rst_specific, output)
        output = self._heading1_re.sub(self._heading1, output)
        output = self._heading2_re.sub(self._heading2, output)
        output = self._heading3_re.sub(self._heading3, output)
        output = self._heading4_re.sub(self._heading4, output)
        output = self._list_re.sub(self._list, output)
        return output
