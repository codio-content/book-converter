import re

ifhtml_re = re.compile(
    r"""\\ifhtmloutput(?P<if_block>.*?)\\fi""", flags=re.DOTALL + re.VERBOSE
)

ifmobile_re = re.compile(
    r"""\\ifmobioutput(?P<if_block>.*?)\\fi""", flags=re.DOTALL + re.VERBOSE
)


class Ignore(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def remove_chars(self, output, chars):
        pos = output.find(chars)
        if pos == -1:
            return output
        level = 0
        for index in range(pos + len(chars), len(output), 1):
            ch = output[index]
            if ch == '}':
                if level == 0:
                    output = output[0:pos] + output[index + 1:]
                    break
                else:
                    level += 1
            elif ch == '{':
                level -= 1
        if chars in output:
            return self.remove_chars(output, chars)
        return output

    def make_block(self, group):
        return ''

    def convert(self):
        output = self.str
        output = self.remove_chars(output, "\\index{")
        output = self.remove_chars(output, "\\label{")
        output = re.sub(r"\\noindent", "", output)
        output = ifhtml_re.sub(self.make_block, output)
        output = ifmobile_re.sub(self.make_block, output)

        return output
