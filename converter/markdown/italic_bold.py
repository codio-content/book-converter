import re


class ItalicBold(object):
    def __init__(self, latex_str):
        self.str = latex_str

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = re.sub(r"\\\\", r"\\", block_contents)
        return "_**{}**_".format(block_contents)

    def convert(self):
        output = self.str
        output = re.compile(r"\\w(\[.*\])?{(?P<block_contents>.*?)}").sub(self.make_block, output)
        output = re.compile(r"\\x{(?P<block_contents>.*?)}").sub(self.make_block, output)

        return output
