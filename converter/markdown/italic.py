import re


class Italic(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        output = re.sub(r"\\emph{(.*?)}", r"<i>\1</i>", output, flags=re.DOTALL)
        output = re.sub(r"{\\em[ ](.*?)}", r"<i>\1</i>", output, flags=re.DOTALL)
        output = re.sub(r"{\\it[ ](.*?)}", r"<i>\1</i>", output, flags=re.DOTALL)

        return output
