import re


class Bold(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str
        output = re.sub(r"\\textbf{(.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"{\\bf[ ](.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"{\\sf[ ](.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"\\B{(.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"\\C{(.*?)}", r"**\1**", output, flags=re.DOTALL + re.VERBOSE)

        return output
