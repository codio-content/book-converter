import re


class InlineMath(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        output = re.sub(r"\\\[ (.*?)\\runtime(.*?) \\\]", r"\[ \1runtime\2 \]", output)
        output = re.sub(r"\\\[ (.*?) \\\]", r"$ \1 $", output)

        return output
