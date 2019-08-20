import re


class InlineCodeBlock(object):
    def __init__(self, latex_str, percent_token):
        self.str = latex_str
        self.token = percent_token

    def _inline_code_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = re.sub(r"\\\\", r"\\", block_contents)
        block_contents = re.sub(r"%", self.token, block_contents)
        return "`{}`".format(block_contents)

    def convert(self):
        output = self.str
        output = re.compile(r"\\java{(?P<block_contents>.*?)}").sub(self._inline_code_block, output)
        output = re.compile(r"\\redis{(?P<block_contents>.*?)}").sub(self._inline_code_block, output)
        output = re.compile(r"\\verb\"(?P<block_contents>.*?)\"").sub(self._inline_code_block, output)
        output = re.compile(r"\\verb'(?P<block_contents>.*?)'").sub(self._inline_code_block, output)
        output = re.compile(r"\\texttt{(?P<block_contents>.*?)}").sub(self._inline_code_block, output)
        output = re.compile(r"{\\tt (?P<block_contents>.*?)}").sub(self._inline_code_block, output)
        return output
