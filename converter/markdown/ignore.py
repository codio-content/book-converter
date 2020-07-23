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
                    output = output[0:pos].lstrip('\n') + output[index + 1:]
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
        output = re.sub(r"\\index\n{(.*?)}", r"\\index{\1}", output, flags=re.DOTALL)
        output = self.remove_chars(output, "\\index{")
        output = self.remove_chars(output, "\\label{")
        output = self.remove_chars(output, "\\vspace{")
        output = re.sub(r"\\noindent", "", output)
        output = re.sub(r"\\bigconcepts", "", output)
        output = re.sub(r"\\prereqs?", "", output)
        output = re.sub(r"\\relax", "", output)
        output = re.sub(r"\\vfill", "", output)
        output = re.sub(r"\\indent", "", output)
        output = re.sub(r"\\fallaciesandpitfalls", "", output)
        output = re.sub(r"\\makebox\[.*?\]{}", "<br/>", output)
        output = re.sub(r"\\hspace{.*?}", "", output)
        output = re.sub(r"\s\\n\n", "", output)
        output = re.sub(r"\\fbox{(.*?\\end{minipage}\n)}\n", r"\1", output, flags=re.DOTALL)
        output = re.sub(r"\\begin{minipage}{.*?}", "", output)
        output = re.sub(r"\\end{minipage}", "", output)
        output = re.sub(r"\\newcommand{.*?}{.*?}", "", output)
        output = re.sub(r"\\ifhtmloutput.*?(\\hfill\\begin{tabular}{\|.*?\|}).*?\\fi", r"\1", output, flags=re.DOTALL)
        output = re.sub(r"\\ifhtmloutput%.*?(\\end{tabular}).*?\\fi", r"\1", output, flags=re.DOTALL)
        output = re.sub(r"\\ifhtmloutput.*?(\\begin{tabular}.*?)\\else(.*?)\\fi", r"\2", output, flags=re.DOTALL)
        output = re.sub(r"\\ifmobioutput.*?(\\begin{tabular}.*?)\\else(.*?)\\fi", r"\2", output, flags=re.DOTALL)
        output = ifhtml_re.sub(self.make_block, output)
        output = ifmobile_re.sub(self.make_block, output)

        return output
