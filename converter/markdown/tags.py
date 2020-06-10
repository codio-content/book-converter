import re


class Tags(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str

        output = re.sub(r"\\tl", r"&lt;", output)
        output = re.sub(r"\\tg", r"&gt;", output)

        return output
