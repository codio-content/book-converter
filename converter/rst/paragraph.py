import re


class Paragraph(object):
    def __init__(self, source_string):
        self.str = source_string
        self._paragraph_re = re.compile(r"""^(?!\s|\d\. |#\. |\* |- |\.\. ).*?(?=\n^\s*$)""",
                                        flags=re.MULTILINE + re.DOTALL)

    @staticmethod
    def _paragraph(matchobj):
        content = matchobj.group(0)
        content = content.replace('\n', ' ')
        return content

    def convert(self):
        output = self.str
        output = self._paragraph_re.sub(self._paragraph, output)
        return output
