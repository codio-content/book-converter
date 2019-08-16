import re


class Ignore(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        output = re.sub(r"\\index{(.*?)}", "", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"\\label{(.*?)}", "", output, flags=re.DOTALL + re.VERBOSE)

        return output
