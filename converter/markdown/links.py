import re


def _clean_block(matchobj):
    block_link = matchobj.group(1)
    block_name = matchobj.group(2)
    block_link = re.sub(r"[~]", "", block_link)
    return f"[{block_name}]({block_link})"


class Links(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def convert(self):
        output = self.str

        output = re.sub(r"\\weblink{(.*?)}\s*?{((.*?\n*.*?)*)}", _clean_block, output)
        output = re.sub(r"\\weblink{(.*?)}", r"[\1](\1)", output)
        output = re.sub(r"\\url{(.*?)}", r"[\1](\1)", output)
        output = re.sub(r"\\href{(.*?)}{(\\[a-z]+)?\s?(.*?)}", r"[\3](\1)", output)

        return output
