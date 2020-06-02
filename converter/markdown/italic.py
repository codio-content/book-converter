import re


class Italic(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        output = re.sub(r"\\emph{(.*?)}", lambda match: f"*{match.group(1).strip()}*", output, flags=re.DOTALL)
        output = re.sub(r"{\\em[ ](.*?)}", r"*\1*", output, flags=re.DOTALL)
        output = re.sub(r"{\\it[ ](.*?)}", r"*\1*", output, flags=re.DOTALL)

        return output
