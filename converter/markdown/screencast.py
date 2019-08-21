import re
import uuid

from converter.markdown.text_as_paragraph import TextAsParagraph
from converter.markdown.block_matcher import match_block

screencast_re = re.compile(
    r"""\\screencast(\[(?P<hash>.*?)])(\s+)?{(?P<tag>.*?)}(\s+)?{(?P<name>.*?)}(\s+)?{(?P<path>.*?)}""",
    flags=re.DOTALL + re.VERBOSE
)


class Screencast(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)
        self._matches = []

    def make_block(self, matchobj):
        youtube_hash = matchobj.group('hash')
        name = matchobj.group('name')

        replace_token = str(uuid.uuid4())

        self._matches.append(replace_token)

        caret_token = self._caret_token
        return f'<hr>{caret_token}**Screencast: {name}**{caret_token}<iframe width="560" height="315" ' \
            f'src="//www.youtube.com/embed/{youtube_hash}" frameborder="0" allowfullscreen>' \
            f'</iframe>{caret_token}{replace_token}'

    def make_content(self, line):
        caret_token = self._caret_token
        line = self.to_paragraph(line)
        return f"{line}{caret_token}<hr>{caret_token}"

    def convert(self):
        output = self.str

        output = screencast_re.sub(self.make_block, output)

        for token in self._matches:
            output = match_block(token, output, self.make_content)

        return output
