import re


class Quotes(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        output = re.sub("``", "“", output)
        output = re.sub("''", "”", output)
        return output
