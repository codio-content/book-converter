import re

from collections import defaultdict


class Header(object):
    def __init__(self, latex_str):
        self.str = latex_str

        self._header_re = re.compile(r"""\\(?P<header_name>chapter|section|subsection|subsubsection*?) # Header
                                    \**{(?P<header_contents>.*?)}""",  # Header title
                                     flags=re.DOTALL + re.VERBOSE)
        self._block_counter = defaultdict(lambda: 1)
        self._block_configuration = {
            "chapter": {
                "markdown_heading": "##",
                "pretty_name": "",
                "show_count": False
            },
            "section": {
                "markdown_heading": "###",
                "pretty_name": "",
                "show_count": False
            },
            "subsection": {
                "markdown_heading": "####",
                "pretty_name": "",
                "show_count": False
            },
            "subsubsection": {
                "markdown_heading": "#####",
                "pretty_name": "",
                "show_count": False
            }
        }

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

    def _replace_header(self, matchobj):
        header_name = matchobj.group('header_name')
        header_contents = matchobj.group('header_contents')

        header = self._format_block_name(header_name)

        block_config = self._block_configuration[header_name]

        separator = "-" if block_config.get("show_count") else ""

        output_str = "{header} {separator} {title}\n".format(
            header=header,
            title=header_contents,
            separator=separator)

        return output_str

    def convert(self):
        output = self.str
        output = self._header_re.sub(self._replace_header, output)

        return output
