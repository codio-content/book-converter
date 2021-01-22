import re


class MathBlock(object):
    def __init__(self, source_string, caret_token, math_block_separator_token):
        self.str = source_string
        self._caret_token = caret_token
        self._math_block_separator_token = math_block_separator_token
        self._math_block_re = re.compile(r"""^[ ]*\.\. math::[ ]*\n{0,2}(?P<content>(.+\n)+)?""", flags=re.MULTILINE)

    def _math_block(self, matchobj):
        out = ""
        content = matchobj.group('content')
        content = content.replace("\n", " ")
        arr = content.split(self._math_block_separator_token)
        for item in arr:
            item = item.strip()
            item = item.replace("...", ". . .")
            item = item.replace("&&", "")
            item = item.replace("&=&", "=")
            item = item.replace("$", "")
            item = f'<center style="font-size: 80%;">${item}$</center>'
            out = out + item + self._caret_token
        return out + "\n"

    def convert(self):
        output = self.str
        output = self._math_block_re.sub(self._math_block, output)
        return output
