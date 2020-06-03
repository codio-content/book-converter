import re


class UnEscape(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str

        output = re.sub(r"\\#", "#", output)
        output = re.sub(r"\\-", "-", output)
        output = re.sub(r"\\\$", r"<span>\$</span>", output)

        return output
