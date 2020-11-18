import logging
import pathlib
import re
import uuid

from collections import namedtuple

from converter.rst.table import Table
from converter.rst.image import Image
from converter.rst.sidebar import Sidebar
from converter.rst.external_link import ExternalLink
from converter.rst.footnote import Footnote
from converter.rst.heading import Heading
from converter.rst.definition import Definition
from converter.rst.inlineav import InlineAv
from converter.rst.avembed import AvEmbed

AssessmentData = namedtuple('AssessmentData', ['id', 'name', 'type', 'points', 'ex_data'])
OPEN_DSA_CDN = 'https://global.codio.com/opendsa/v3'


class Rst2Markdown(object):
    def __init__(self, lines_array, exercises, workspace_dir=pathlib.Path('.'), chapter_num=0, subsection_num=0):
        self._caret_token = str(uuid.uuid4())
        self._chapter_num = chapter_num
        self._subsection_num = subsection_num
        self._figure_counter = 0
        self._assessments = list()
        self._iframe_images = list()
        self.lines_array = lines_array
        self._exercises = exercises
        self.workspace_dir = workspace_dir
        self._list_re = re.compile(r"""^( *)(?P<type>[*+\-]|[0-9#]+[\.]) [^\n]*(?:\n(?!\1\2|\S)[^\n]*)*""",
                                   flags=re.MULTILINE)
        self._ext_links_re = re.compile(r"""`(?P<name>.*?)\n?<(?P<ref>https?:.*?)>`_""")
        self._ref_re = re.compile(r""":(ref|chap):`(?P<name>.*?)(?P<label_name><.*?>)?`""", flags=re.DOTALL)
        self._term_re = re.compile(r""":term:`(?P<name>.*?)(<(?P<label_name>.*?)>)?`""", flags=re.DOTALL)
        self._math_re = re.compile(r""":math:`(?P<content>.*?)`""")
        self._math_block_re = re.compile(r""" {,3}.. math::\n^[\s\S]*?(?P<content>.*?)(?=\n{2,})""",
                                         flags=re.MULTILINE + re.DOTALL)
        self._todo_block_re = re.compile(r"""\.\. TODO::\n(?P<options>^ +:.*?: \S*\n$)(?P<text>.*?\n^$\n(?=\S*)|.*)""",
                                         flags=re.MULTILINE + re.DOTALL)
        self._paragraph_re = re.compile(r"""^(?!\s|\d\. |#\. |\* |- |\.\. ).*?(?=\n^\s*$)""",
                                        flags=re.MULTILINE + re.DOTALL)
        self._topic_re = re.compile(
            r"""^\.{2} topic:{2} +(?P<type>.*?)\n(?P<content>(?:\n* +[^\n]+\n*)*)""", flags=re.MULTILINE + re.DOTALL)
        self._tip_re = re.compile(
            r"""^\.{2} tip:{2} *\n(?P<content>(?:\n* +[^\n]+\n*)*)""", flags=re.MULTILINE)
        self._epigraph_re = re.compile(r"""[ ]*\.\. epigraph:: *\n*(?P<content>(?: +[^\n]+\n*)*)""")
        self._code_include_re = re.compile(r"""\.\. codeinclude:: (?P<path>.*?)\n(?P<options>(?: +:.*?: \S*\n)+)?""")
        self._extrtoolembed_re = re.compile(
            r"""^$\n^.*?\n-+\n\n?\.\. extrtoolembed:: '(?P<name>.*?)'\n( *:.*?: .*?\n)?(?=\S|$)""", flags=re.MULTILINE)
        self._term_def_re = re.compile(r"""^:(?P<term>[^:\n]+): *\n(?P<content>(?: +[^\n]+\n*)*)""", flags=re.MULTILINE)
        self._lineblock_re = re.compile(r"""^((?: {2,})?\|)[^\n]*(?:\n(?:\1| {2,})[^\n]+)*""", flags=re.MULTILINE)

    def _list(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group(0)
        content = content.strip()
        items = []
        match_all_items = list(re.finditer(r'^( *)([*+-]|[0-9#]+[.]) [\s\S]+?(?:\n{2,}(?! )(?!\1\2 |\S)\n*|\s*$)',
                                           content, flags=re.MULTILINE))
        if len(match_all_items) > 1:
            for item in match_all_items:
                item = f'{item.group(0)}{caret_token}'
                item = self._clearing_line_breaks(item)
                items.append(item)
            content = '\n'.join(items)
        else:
            content = self._clearing_text_spaces(content)
            content = self._clearing_line_breaks(content)
        return content

    def _clearing_text_spaces(self, data):
        space = re.search('\n *', data)
        if space:
            space_count = len(space.group(0))
            space_regex = f"\n^ {{{space_count}}}"
            data = re.sub(space_regex, '', data, flags=re.MULTILINE)
        return data

    def _clearing_line_breaks(self, data):
        out = []
        for line in data.split('\n'):
            out.append(line)
        return ' '.join(out)

    def _ext_links(self, matchobj):
        name = matchobj.group('name')
        ref = matchobj.group('ref')
        name = name.strip()
        return f'[{name}]({ref})'

    def _ref(self, matchobj):
        name = matchobj.group('name')
        name = name.strip()
        label_name = matchobj.group('label_name')
        return f'Chapter: **{name}**'

    def _term(self, matchobj):
        name = matchobj.group('name')
        name = name.strip()
        label_name = matchobj.group('label_name')
        return f'**{name}**'

    def _math(self, matchobj):
        content = matchobj.group('content')
        content = content.replace("\\+", "+")
        return f'$${content}$$'

    def _math_block(self, matchobj):
        content = matchobj.group('content')
        content = content.strip()
        content = content.replace("\\+", "+")
        return f'<center>$${content}$$</center>'

    def _paragraph(self, matchobj):
        content = matchobj.group(0)
        content = content.replace('\n', ' ')
        return content

    def _topic(self, matchobj):
        caret_token = self._caret_token
        topic_type = matchobj.group('type')
        content = matchobj.group('content')
        content = re.sub(r"\n +", "\n ", content)
        self._figure_counter += 1
        return f'<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**{topic_type} {self._chapter_num}.{self._subsection_num}.' \
               f'{self._figure_counter}**<br/>' \
               f'{caret_token}{caret_token}{content}</div><br/>{caret_token}{caret_token}'

    def _tip(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        return f'<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**Tip**{caret_token}{caret_token}{content}' \
               f'</div><br/>{caret_token}{caret_token}'

    def _epigraph(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        content = content.strip()
        out = []
        for line in content.split('\n'):
            line = line.strip()
            out.append(line)
        content = '\n'.join(out)
        return f'<div style="padding: 10px 30px;">{caret_token}{content}{caret_token}</div>{caret_token}{caret_token}'

    def _lineblock(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group(0)
        content = re.sub(r'^( *\| ?| {2,})', '', content, flags=re.MULTILINE)
        out = []
        for line in content.split('\n'):
            line = line.strip()
            out.append(f' {line}')
        content = '\n'.join(out)
        return f' <div style="padding-left: 50px;">{caret_token}{content}{caret_token} </div>{caret_token}'

    def _todo_block(self, matchobj):
        return ''

    def _code_lines(self, data):
        flag = False
        lines = data.split("\n")
        for ind, line in enumerate(lines):
            prev_line = lines[ind - 1]
            next_line = lines[ind + 1] if ind + 1 < len(lines) else ''
            indent_size = len(line) - len(line.lstrip())
            if not prev_line.strip() and line.strip():
                if indent_size == 2 or indent_size == 3:
                    flag = True
            if flag and not line.strip().startswith(":"):
                lines[ind] = line.replace(line, f"```{line}```")
            if flag:
                if not next_line.strip() or indent_size < 2:
                    flag = False
        return "\n".join(lines)

    def _extrtoolembed(self, matchobj):
        name = matchobj.group('name').lower()
        ex_data = self._exercises.get(name.lower(), {})
        assessment_id = f'test-{name.lower()}'
        if not ex_data:
            return ''
        assessment = AssessmentData(assessment_id, name, 'test', 20, ex_data)
        self._assessments.append(assessment)
        return ''

    def _code_include(self, matchobj):
        options = {}
        lines = []
        content = ''
        tag = None
        caret_token = self._caret_token
        curr_dir = self.workspace_dir
        code_dir = curr_dir.joinpath('SourceCode')
        option_re = re.compile('[\t ]+:([^:]+): (.+)')
        path = matchobj.group('path').strip()
        path = pathlib.Path(path)
        opt = matchobj.group('options')
        if opt:
            opt = opt.split('\n')
            for item in opt:
                match = option_re.match(item)
                if match:
                    options[match[1]] = match[2]
                    tag = options.get('tag', '')
        file_path = pathlib.Path(path)
        if not str(file_path).endswith(".java"):
            file_path = "{}.java".format(file_path)
        if not str(file_path).startswith('Java'):
            java_dir = pathlib.Path('Java')
            file_path = java_dir.joinpath(file_path)
        file = code_dir.joinpath(file_path).resolve()
        try:
            lines = self.load_file(file)
        except BaseException as e:
            logging.error(e)
        if lines:
            for line in lines:
                if not line:
                    continue
                if tag:
                    start_tag_string = f'/* *** ODSATag: {tag} *** */'
                    end_tag_string = f'/* *** ODSAendTag: {tag} *** */'
                    if line.strip().startswith(start_tag_string):
                        content = ''
                        continue
                    if line.strip().startswith(end_tag_string):
                        return f'{caret_token}```{caret_token}{content}{caret_token}```{caret_token}{caret_token}'
                line = re.sub(r"/\* \*\*\* .*? \*\*\* \*/", "", line)
                content += line
        return f'{caret_token}```{caret_token}{content}{caret_token}```{caret_token}{caret_token}'

    def _enum_lists_parse(self, lines):
        counter = 0
        list_flag = False
        for ind, line in enumerate(lines):
            next_line = lines[ind + 1] if ind + 1 < len(lines) else ''
            if line.startswith('#. ') or line.startswith('   #. '):
                list_flag = True
                counter += 1
                lines[ind] = line.replace("#", str(counter), 1)
            if next_line[:1].strip() and not next_line.startswith('#. ') \
                    and not next_line.startswith('   #. ') and list_flag:
                list_flag = False
                counter = 0
        return lines

    def get_figure_counter(self):
        return self._figure_counter

    def load_file(self, path):
        with open(path, 'r') as file:
            return file.readlines()

    def get_assessments(self):
        return self._assessments

    def get_iframe_images(self):
        return self._iframe_images

    def to_markdown(self):
        self.lines_array = self._enum_lists_parse(self.lines_array)
        output = '\n'.join(self.lines_array)
        # output = re.sub(r".. _[\S ]+:", "", output)  # todo: line moved below. removes tags for images
        output = re.sub(r"\|---\|", "--", output)
        output = re.sub(r"\+\+", "\\+\\+", output)
        output = re.sub(r"^\|$", "<br/>", output, flags=re.MULTILINE)
        output = self._extrtoolembed_re.sub(self._extrtoolembed, output)
        output = Heading(output, self._caret_token).convert()
        output = Definition(output, self._caret_token).convert()
        output = self._lineblock_re.sub(self._lineblock, output)
        output = self._topic_re.sub(self._topic, output)
        output = self._tip_re.sub(self._tip, output)
        output = Image(output, self._caret_token, self._chapter_num, self._subsection_num).convert()
        output = re.sub(r".. _[\S ]+:", "", output)  # todo: line moved below. removes tags for images
        output, figure_counter, iframe_images = InlineAv(output, self._caret_token,
                                                         self.workspace_dir, self._chapter_num,
                                                         self._subsection_num, OPEN_DSA_CDN,
                                                         self._figure_counter
                                                         ).convert()
        if figure_counter:
            self._figure_counter = figure_counter

        if iframe_images:
            self._iframe_images.extend(iframe_images)

        output, assessments = AvEmbed(output, self._caret_token, OPEN_DSA_CDN).convert()
        if assessments:
            self._assessments.extend(assessments)
        output = self._list_re.sub(self._list, output)
        output = self._ext_links_re.sub(self._ext_links, output)
        output = self._ref_re.sub(self._ref, output)
        output = self._term_re.sub(self._term, output)
        output = self._math_re.sub(self._math, output)
        output = self._math_block_re.sub(self._math_block, output)
        output = self._epigraph_re.sub(self._epigraph, output)
        output = self._paragraph_re.sub(self._paragraph, output)
        output = Sidebar(output, self._caret_token).convert()
        output = Table(output).convert()
        output = ExternalLink(output).convert()
        output = self._code_lines(output)
        output = self._code_include_re.sub(self._code_include, output)
        output = self._todo_block_re.sub(self._todo_block, output)
        output = Footnote(output).convert()
        output = re.sub(self._caret_token, "\n", output)
        return output
