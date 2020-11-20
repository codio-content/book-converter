import pathlib
import re
import uuid

from converter.rst.avembed import AvEmbed
from converter.rst.bibliography import Bibliography
from converter.rst.code_include import CodeInclude
from converter.rst.comment import Comment
from converter.rst.definition import Definition
from converter.rst.epigraph import Epigraph
from converter.rst.external_link import ExternalLink
from converter.rst.extrtoolembed import ExtrToolEmbed
from converter.rst.footnote import Footnote
from converter.rst.heading import Heading
from converter.rst.image import Image
from converter.rst.indented_code import IndentedCode
from converter.rst.inlineav import InlineAv
from converter.rst.line_block import LineBlock
from converter.rst.list import List
from converter.rst.match import Match
from converter.rst.only import Only
from converter.rst.paragraph import Paragraph
from converter.rst.ref import Ref
from converter.rst.sidebar import Sidebar
from converter.rst.table import Table
from converter.rst.term import Term
from converter.rst.tip import Tip
from converter.rst.todo_block import TodoBlock
from converter.rst.topic import Topic
from converter.rst.simple_table import SimpleTable

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

    def _enum_lists_parse(self, lines):
        counter = 0
        list_flag = False
        for ind, line in enumerate(lines):
            next_line = lines[ind + 1] if ind + 1 < len(lines) else ''
            if self.bullet_match(line):
                list_flag = True
                counter += 1
                lines[ind] = line.replace("#", str(counter), 1)
            if next_line[:1].strip() and not self.bullet_match(next_line) and list_flag:
                list_flag = False
                counter = 0
        return lines

    @staticmethod
    def bullet_match(line):
        return re.search(r'^ *#[.|)] ', line)

    def get_figure_counter(self):
        return self._figure_counter

    @staticmethod
    def load_file(path):
        with open(path, 'r') as file:
            return file.readlines()

    def get_assessments(self):
        return self._assessments

    def get_iframe_images(self):
        return self._iframe_images

    def to_markdown(self):
        self.lines_array = self._enum_lists_parse(self.lines_array)
        output = '\n'.join(self.lines_array)
        output = re.sub(r"\|---\|", "--", output)
        output = re.sub(r"\+\+", "\\+\\+", output)
        output = re.sub(r"^\|$", "<br/>", output, flags=re.MULTILINE)
        output, assessments = ExtrToolEmbed(output, self._exercises).convert()
        if assessments:
            self._assessments.extend(assessments)

        output = Heading(output, self._caret_token).convert()
        output = Definition(output, self._caret_token).convert()
        output = TodoBlock(output).convert()
        output, figure_counter = Topic(output, self._caret_token,
                                       self._chapter_num, self._subsection_num,
                                       self._figure_counter).convert()
        if figure_counter:
            self._figure_counter = figure_counter

        output = Tip(output, self._caret_token).convert()
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

        output = List(output, self._caret_token).convert()
        output = Ref(output).convert()
        output = Term(output).convert()
        output = Match(output).convert()
        output = SimpleTable(output, self._caret_token).convert()
        output = Epigraph(output, self._caret_token).convert()
        output = Paragraph(output).convert()
        output = Table(output).convert()
        output = LineBlock(output, self._caret_token).convert()
        output = Sidebar(output, self._caret_token).convert()
        output = ExternalLink(output).convert()
        output = Only(output).convert()
        output = IndentedCode(output, self._caret_token).convert()
        output = CodeInclude(output, self._caret_token, self.workspace_dir, self.load_file).convert()
        output = Footnote(output).convert()
        output = Bibliography(output, self._caret_token).convert()
        # output = Comment(output).convert()
        output = re.sub(self._caret_token, "\n", output)
        return output
