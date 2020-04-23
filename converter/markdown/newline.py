import re


class NewLine(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        output = re.sub(r"^\\\\ ", "<br/>", output, flags=re.MULTILINE)
        output = re.sub(r"\\newline ", "<br/>", output, flags=re.MULTILINE)
        output = re.sub(r"\\newline<", "<br/><", output, flags=re.MULTILINE)
        output = re.sub(r"\\newline$", "<br/>", output, flags=re.MULTILINE)

        return output
