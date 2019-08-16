import re
from collections import defaultdict
from collections import namedtuple

Code = namedtuple('Code', ['name', 'source'])


class LaTeX2Markdown(object):
    """Initialise with a LaTeX string - see the main routine for examples of
    reading this string from an existing .tex file.
    To modify the outputted markdown, modify the _block_configuration variable
    before initializing the LaTeX2Markdown instance."""

    def _make_paragraphs(self, lines):
        processed = []
        current = ''
        single_line = ('\\chapter', '\\section', '\\index', '%')
        is_multi_line = False
        for line in lines:
            if line.strip().startswith(single_line) or '%' in line:
                if current:
                    processed.append(current)
                    current = ''
                if line.strip().startswith('%'):
                    processed.append(line.strip())
                else:
                    processed.append(line)
                continue
            elif line.startswith('\\begin'):
                if current:
                    processed.append(current)
                    current = ''
                is_multi_line = True
                processed.append(line)
                continue
            elif not line:
                if current:
                    processed.append(current)
                    current = ''
                processed.append(line)
                continue

            if is_multi_line:
                processed.append(line)
            else:
                if current:
                    current += ' ' + line
                else:
                    current = line
            if line.startswith('\\end'):
                is_multi_line = False
        if current:
            processed.append(current)
        return processed

    def __init__(
        self, latex_array, refs={}, chapter_num=1, figure_num=0,
        exercise_num=0, remove_trinket=False, remove_exercise=False,
        detect_asset_ext=lambda _: _
    ):
        latex_string = '\n'.join(self._make_paragraphs(latex_array))
        self._refs = refs
        self._chapter_num = chapter_num
        self._exercise_counter = 0
        self._figure_counter = 0
        self._figure_counter_offset = figure_num
        self._exercise_counter_offset = exercise_num
        self._block_configuration = _block_configuration
        self._latex_string = latex_string
        self._block_counter = defaultdict(lambda: 1)
        self._pdfs = []
        self._source_codes = []
        self._remove_trinket = remove_trinket
        self._remove_exercise = remove_exercise
        self.detect_asset_ext = detect_asset_ext

        # Precompile the regexes





    def _replace_header(self, matchobj):
        """Creates a header string for a section/subsection/chapter match.
        For example, "### 2 - Integral Calculus\n" """

        header_name = matchobj.group('header_name')
        header_contents = matchobj.group('header_contents')

        header = self._format_block_name(header_name)

        block_config = self._block_configuration[header_name]

        # If we have a count, separate the title from the count with a dash
        separator = "-" if block_config.get("show_count") else ""

        output_str = "{header} {separator} {title}\n".format(
            header=header,
            title=header_contents,
            separator=separator)

        return output_str

    def _replace_block(self, matchobj):
        """Create a string that replaces an entire block.
        The string consists of a header (e.g. ### Exercise 1)
        and a block, containing the LaTeX code.
        The block may be optionally indented, blockquoted, etc.
        These settings are customizable through the config.json
        file"""

        block_name = matchobj.group('block_name')
        block_contents = matchobj.group('block_contents')
        # Block title may not exist, so use .get method
        block_title = matchobj.groupdict().get('block_title')

        # We have to format differently for lists
        if block_name in {"itemize", "enumerate", "description"}:
            formatted_contents = self._format_list_contents(block_name,
                                                            block_contents)
        else:
            formatted_contents = self._format_block_contents(block_name,
                                                             block_contents)

        header = self._format_block_name(block_name, block_title)

        output_str = "{header}\n\n{block_contents}".format(
            header=header,
            block_contents=formatted_contents)
        if block_name == "description":
            output_str = "{header}{block_contents}".format(
                header=header,
                block_contents=formatted_contents)
        return output_str

    def _format_block_contents(self, block_name, block_contents):
        """Format the contents of a block with configuration parameters
        provided in the self._block_configuration attribute"""

        block_config = self._block_configuration[block_name]

        line_indent_char = block_config["line_indent_char"]

        output_str = ""
        for line in block_contents.lstrip().rstrip().split("\n"):
            line = line.lstrip().rstrip()
            line = line.replace("\\\\", "<br/>")
            indented_line = line_indent_char + line + "\n"
            output_str += indented_line
        return output_str

    def _format_list_contents(self, block_name, block_contents):
        block_config = self._block_configuration[block_name]

        list_heading = block_config["list_heading"]

        output_str = ""
        for line in block_contents.lstrip().rstrip().split("\n"):
            line = line.lstrip().rstrip()
            line = line.replace("\\\\", "<br/>")

            markdown_list_line = line.replace(r"\item", list_heading)
            if not line:
                continue
            if "\\term" in line:
                if output_str:
                    output_str = output_str.strip() + "\n"
                markdown_list_line = markdown_list_line.replace("\\term", list_heading)
                markdown_list_line = markdown_list_line.replace("{", "**")
                markdown_list_line = markdown_list_line.replace("}", "**")
            elif "\\item" in line:
                if output_str:
                    output_str = output_str.strip() + "\n"
                markdown_list_line = markdown_list_line.replace("[", "**")
                markdown_list_line = markdown_list_line.replace("]", "**")
            output_str += markdown_list_line + ' '
        return output_str

    def _format_block_name(self, block_name, block_title=None):
        """Format the Markdown header associated with a block.
        Due to the optional block_title, we split the string construction
        into two parts."""

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



    def _eqnarray_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = re.sub(r"^&& {2}", "", block_contents, flags=re.MULTILINE)
        block_contents = re.sub(r"^& ", "", block_contents, flags=re.MULTILINE)
        block_contents = re.sub(r" &$", "", block_contents, flags=re.MULTILINE)
        block_contents = re.sub(r" & \\\\$", " \\\\\\\\", block_contents, flags=re.MULTILINE)
        return "$${}$$".format(block_contents, flags=re.MULTILINE)

    def _makequotation_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_author = matchobj.group('block_author')
        block_contents = ' '.join(block_contents.split('\n'))

        return '> {}\n>\n> __{}__'.format(block_contents, block_author)



    def _code_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        try:
            file_name = matchobj.group('file_name')
            self._source_codes.append(Code(file_name, block_contents))
        except IndexError:
            pass
        block_name = matchobj.group('block_name')
        if self._remove_trinket and block_name == 'trinket':
            return ''
        # % in code block is not latex comments, escape it and replace later
        block_contents = re.sub(r"%", r"\\%", block_contents)
        return "```code{}```".format(block_contents)

    def _inline_code_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = re.sub(r"\\\\", r"\\", block_contents)
        return "`{}`".format(block_contents)


    def _latex_to_markdown(self):
        # Reformat, lists, blocks, and headers.
        output = self._block_re.sub(self._replace_block, output)

        return output.lstrip().rstrip()

    def to_markdown(self):
        return self._latex_to_markdown()

    def to_latex(self):
        return self._latex_string

    def get_pdfs_for_convert(self):
        return self._pdfs

    def get_figure_counter(self):
        return self._figure_counter

    def get_exercise_counter(self):
        return self._exercise_counter

    def get_source_codes(self):
        return self._source_codes
