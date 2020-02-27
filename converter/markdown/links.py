import re


class Links(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def _clean_block(self, matchobj):
        block_link = matchobj.group(1)
        block_name = matchobj.group(3)
        block_link = re.sub(r"[~]", "", block_link)
        return f"[{block_name}]({block_link})"

    def convert(self):
        output = self.str

        output = re.sub(r"\\weblink{(.*?)}(.*?)?{(.*?)}", self._clean_block, output, flags=re.DOTALL + re.VERBOSE)
        output = re.sub(r"\\weblink{(.*?)}", r"[\1](\1)", output, flags=re.MULTILINE)
        output = re.sub(r"\\url{(.*?)}", r"[\1](\1)", output)
        output = re.sub(r"\\href{(.*?)}{(\\[a-z]+)?\s?(.*?)}", r"[\1](\3)", output)
        output = re.sub(r"\\href{(.*?)}`(\\[a-z]+)?\s?(.*?)`", r"[\1](\3)", output)

        return output
