import re


class Links(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str

        output = re.sub(r"\\weblink{(.*?)}([\s%])?{(.*?)}", r"[\3](\1)", output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"\\weblink{(.*?)}", r"[\1](\1)", output, flags=re.MULTILINE)
        output = re.sub(r"\\url{(.*?)}", r"[\1](\1)", output)
        output = re.sub(r"\\href{(.*?)}{(\\[a-z]+)?\s?(.*?)}", r"[\3](\1)", output)
        output = re.sub(r"\\href{(.*?)}`(\\[a-z]+)?\s?(.*?)`", r"[\3](\1)", output)

        return output
