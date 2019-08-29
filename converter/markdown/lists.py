import re

from collections import defaultdict
from converter.markdown.text_as_paragraph import TextAsParagraph


class Lists(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

        self._block_counter = defaultdict(lambda: 1)
        self._lists_re = re.compile(r"""\\begin{(?P<block_name>enumerate|itemize|description)} # list name
                                    (\[.*?\])? # Optional enumerate settings i.e. (a)
                                    (?P<block_contents>.*?) # Non-greedy list contents
                                    \\end{(?P=block_name)}""",  # closing list
                                    flags=re.DOTALL + re.VERBOSE)
        self._block_configuration = {
            "enumerate": {
                "line_indent_char": "",
                "list_heading": "1. ",
                "markdown_heading": "",
                "pretty_name": "",
                "show_count": False
            },
            "itemize": {
                "line_indent_char": "",
                "list_heading": "* ",
                "markdown_heading": "",
                "pretty_name": "",
                "show_count": False
            },
            "description": {
                "line_indent_char": "",
                "list_heading": "* ",
                "markdown_heading": "",
                "pretty_name": "",
                "show_count": False
            }
        }

    def _format_list_contents(self, block_name, block_contents):
        block_config = self._block_configuration[block_name]

        list_heading = block_config["list_heading"]

        output_str = ""
        for line in block_contents.lstrip().rstrip().split("\n"):
            line = line.lstrip().rstrip()
            line = line.replace("\\\\", "<br/>")

            markdown_list_line = re.sub(r"\\item(\s+)?", list_heading, line)
            if not line:
                continue
            if "\\term" in line:
                if output_str:
                    output_str = output_str.strip() + self._caret_token
                markdown_list_line = markdown_list_line.replace("\\term", list_heading)
                if "\\term{" in line:
                    markdown_list_line = markdown_list_line.replace("{", "**", 1)
                    markdown_list_line = markdown_list_line.replace("}", "**", 1)
            elif "\\item" in line:
                if output_str:
                    output_str = output_str.strip() + self._caret_token
                if "\\item[" in line:
                    markdown_list_line = markdown_list_line.replace("[", "**", 1)
                    markdown_list_line = markdown_list_line.replace("]", "**", 1)
            output_str += markdown_list_line + ' '
        return output_str

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

        if '\\begin{enumerate' in block_contents or '\\begin{itemize' in block_contents:
            block_contents = self._lists_re.sub(self._replace_block, block_contents)

        formatted_contents = self._format_list_contents(block_name, block_contents)
        formatted_contents = self.to_paragraph(formatted_contents)

        header = self._format_block_name(block_name, block_title)
        caret_token = self._caret_token

        output_str = f"{header}{caret_token}{caret_token}{formatted_contents}{caret_token}{caret_token}"
        if block_name == "description":
            output_str = f"{header}{formatted_contents}{caret_token}{caret_token}"
        return output_str

    def convert(self):
        output = self.str
        output = self._lists_re.sub(self._replace_block, output)

        return output
