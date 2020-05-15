import re

from collections import defaultdict
from converter.markdown.text_as_paragraph import TextAsParagraph


class Block(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)
        self._block_counter = defaultdict(lambda: 1)

        self._block_re = re.compile(r"""\\begin{(?P<block_name>exer|proof|thm|lem|prop|quote|quotation)} # block name
                                    (\[(?P<block_title>.*?)\])? # Optional block title
                                    (?P<block_contents>.*?) # Non-greedy block contents
                                    \\end{(?P=block_name)}""",  # closing block
                                    flags=re.DOTALL + re.VERBOSE)

        self._block_configuration = {
            "exer": {
                "line_indent_char": "> ",
                "markdown_heading": "####",
                "pretty_name": "Exercise",
                "show_count": True
            },
            "lem": {
                "line_indent_char": "> ",
                "markdown_heading": "####",
                "pretty_name": "Lemma",
                "show_count": True
            },
            "proof": {
                "line_indent_char": "",
                "markdown_heading": "####",
                "pretty_name": "Proof",
                "show_count": False
            },
            "prop": {
                "line_indent_char": "> ",
                "markdown_heading": "####",
                "pretty_name": "Proposition",
                "show_count": True
            },
            "thm": {
                "line_indent_char": "> ",
                "markdown_heading": "####",
                "pretty_name": "Theorem",
                "show_count": True
            },
            "quote": {
                "line_indent_char": "> ",
                "markdown_heading": "",
                "pretty_name": "",
                "show_count": False
            },
            "quotation": {
                "line_indent_char": "> ",
                "markdown_heading": "",
                "pretty_name": "",
                "show_count": False
            }
        }

    def _format_block_contents(self, block_name, block_contents):
        block_config = self._block_configuration[block_name]

        line_indent_char = block_config["line_indent_char"]

        output_str = ""
        for line in block_contents.lstrip().rstrip().split("\n"):
            line = line.lstrip().rstrip()
            line = line.replace("\\\\", "<br/>")
            output_str += f' {line}'
        return line_indent_char + output_str

    def _format_block_name(self, block_name, block_title=None):
        block_config = self._block_configuration[block_name]
        pretty_name = block_config["pretty_name"]
        show_count = block_config["show_count"]
        markdown_heading = block_config["markdown_heading"]

        block_count = self._block_counter[block_name] if show_count else ""
        self._block_counter[block_name] += 1

        output_str = "{markdown_heading} {pretty_name} {block_count}".format(
            markdown_heading=markdown_heading,
            pretty_name=pretty_name,
            block_count=block_count)

        if block_title:
            output_str = "{output_str} ({block_title})".format(
                output_str=output_str,
                block_title=block_title)

        return output_str.lstrip().rstrip()

    def _replace_block(self, matchobj):
        block_name = matchobj.group('block_name')
        block_contents = matchobj.group('block_contents')
        block_title = matchobj.groupdict().get('block_title')

        formatted_contents = self._format_block_contents(block_name, block_contents)
        formatted_contents = self.to_paragraph(formatted_contents)

        header = self._format_block_name(block_name, block_title)

        caret_token = self._caret_token
        return f"{header}{caret_token}{caret_token}{formatted_contents}"

    def convert(self):
        output = self.str
        output = self._block_re.sub(self._replace_block, output)

        return output
