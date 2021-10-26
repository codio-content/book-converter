import uuid
import re

from converter.markdown.footnote import Footnote
from converter.markdown.inline_code_block import InlineCodeBlock
from converter.markdown.code_block import CodeBlock
from converter.markdown.bold import Bold
from converter.markdown.italic import Italic
from converter.markdown.ignore import Ignore
from converter.markdown.saas_specific import SaasSpecific
from converter.markdown.center import Center
from converter.markdown.checkyourself import CheckYouself
from converter.markdown.cite import Cite
from converter.markdown.concepts import Consents
from converter.markdown.elaboration import Elaboration
from converter.markdown.fallacy import Fallacy
from converter.markdown.picfigure import PicFigure
from converter.markdown.pitfall import PitFall
from converter.markdown.summary import Summary
from converter.markdown.quotes import Quotes
from converter.markdown.links import Links
from converter.markdown.newline import NewLine
from converter.markdown.italic_bold import ItalicBold
from converter.markdown.inline_math import InlineMath
from converter.markdown.cleanup import Cleanup
from converter.markdown.exercise import Exercise
from converter.markdown.figure import Figure
from converter.markdown.refs import Refs
from converter.markdown.sidebar import Sidebar
from converter.markdown.eqnarray import EqnArray
from converter.markdown.quotation import Quotation
from converter.markdown.header import Header
from converter.markdown.table import Table
from converter.markdown.lists import Lists
from converter.markdown.block import Block
from converter.markdown.paragraph import Paragraph
from converter.markdown.tablefigure import TableFigure
from converter.markdown.chips import Chips
from converter.markdown.dedicationwithpic import DedicationWithPic
from converter.markdown.codefilefigure import CodeFigure
from converter.markdown.codefile import CodeFile
from converter.markdown.remove_comments import RemoveComments
from converter.markdown.screencast import Screencast
from converter.markdown.tabularx import Tabularx
from converter.markdown.tabular import Tabular
from converter.markdown.unescape import UnEscape
from converter.markdown.vocabulary import Vocabulary


class LaTeX2Markdown(object):
    def __init__(
            self, latex_array, refs={}, chapter_num=1, figure_num=0,
            exercise_num=0, remove_trinket=False, remove_exercise=False,
            detect_asset_ext=lambda _: _, load_workspace_file=lambda _: '',
            code_syntax='code'
    ):
        self._code_syntax = code_syntax
        self._latex_string = '\n'.join(latex_array)
        self._percent_token = str(uuid.uuid4())
        self._caret_token = str(uuid.uuid4())
        self._refs = refs
        self._chapter_num = chapter_num
        self._exercise_counter = 0
        self._figure_counter = 0
        self._figure_counter_offset = figure_num
        self._exercise_counter_offset = exercise_num
        self._pdfs = []
        self._source_codes = []
        self._remove_trinket = remove_trinket
        self._remove_exercise = remove_exercise
        self._detect_asset_ext = detect_asset_ext
        self._load_workspace_file = load_workspace_file

    def increment_figure_counter(self, figure_counter):
        self._figure_counter += figure_counter
        self._figure_counter_offset += figure_counter

    def _latex_to_markdown(self):
        output = self._latex_string

        output = Ignore(output).convert()
        output, footnotes = Footnote(output).convert()
        if footnotes:
            footnotes_text = '\n\n'.join(footnotes)
            output = output + f'\n\n<hr>\n\n{footnotes_text}'
        output, figure_counter = TableFigure(
            output, self._caret_token, self._load_workspace_file,
            self._figure_counter_offset, self._chapter_num, self._refs
        ).convert()
        if figure_counter:
            self.increment_figure_counter(figure_counter)
        output = Quotes(output).convert()
        output = Bold(output).convert()
        output = Italic(output).convert()
        output = SaasSpecific(output, self._caret_token).convert()
        output = ItalicBold(output).convert()
        output, source_codes = CodeBlock(
            output, self._percent_token, self._caret_token, self._remove_trinket, self._code_syntax
        ).convert()
        if source_codes:
            self._source_codes.extend(source_codes)
        output, source_codes, figure_counter = CodeFigure(
            output, self._caret_token, self._percent_token, self._load_workspace_file,
            self._figure_counter_offset, self._chapter_num, self._refs, self._code_syntax
        ).convert()
        if figure_counter:
            self.increment_figure_counter(figure_counter)
        if source_codes:
            self._source_codes.extend(source_codes)
        output, source_codes = CodeFile(
            output, self._caret_token, self._percent_token, self._load_workspace_file, self._code_syntax
        ).convert()
        if source_codes:
            self._source_codes.extend(source_codes)
        output = re.sub(r"\\%", self._percent_token, output)
        output = InlineCodeBlock(output, self._percent_token).convert()

        # remove comments
        output = RemoveComments(output).convert()
        output = Quotation(output, self._caret_token).convert()
        output = Paragraph(output).convert_without_tags()
        output = Refs(output, self._refs).convert()
        output = Links(output).convert()

        output = InlineMath(output).convert()
        output = CheckYouself(output, self._caret_token).convert()
        output = Cite(output, self._load_workspace_file).convert()
        output = Consents(output, self._caret_token).convert()
        output = Elaboration(output, self._caret_token).convert()
        output = Vocabulary(output, self._caret_token).convert()
        output = Fallacy(output, self._caret_token).convert()
        output = PitFall(output, self._caret_token).convert()
        output = Summary(output, self._caret_token).convert()
        output = Chips(output, self._caret_token).convert()
        output = Cleanup(output).convert()

        output, images, figure_counter = PicFigure(
            output, self._caret_token, self._detect_asset_ext,
            self._figure_counter_offset, self._chapter_num, self._refs
        ).convert()
        if figure_counter:
            self.increment_figure_counter(figure_counter)
        if images:
            self._pdfs.extend(images)
        output, images, figure_counter = Figure(
            output, self._figure_counter_offset, self._chapter_num, self._detect_asset_ext, self._caret_token
        ).convert()
        if images:
            self._pdfs.extend(images)
        if figure_counter:
            self.increment_figure_counter(figure_counter)
        output, images = Sidebar(output, self._detect_asset_ext, self._caret_token).convert()
        if images:
            self._pdfs.extend(images)
        output, images = DedicationWithPic(output, self._caret_token).convert()
        if images:
            self._pdfs.extend(images)

        output, exercise_counter = Exercise(
            output, self._exercise_counter_offset, self._chapter_num, self._remove_exercise, self._caret_token
        ).convert()
        if exercise_counter:
            self._exercise_counter += exercise_counter
        output = EqnArray(output).convert()
        output = Screencast(output, self._caret_token).convert()

        output = Header(output).convert()
        output = Tabular(output, self._caret_token).convert()
        output = Tabularx(output, self._caret_token).convert()
        output = Table(output, self._refs, self._caret_token).convert()
        output = Lists(output, self._caret_token).convert()
        output = Block(output, self._caret_token).convert()
        output = Center(output, self._caret_token).convert()

        output = UnEscape(output).convert()
        output = NewLine(output).convert()

        # convert all matched % back
        output = re.sub(self._percent_token, "%", output)
        output = re.sub(self._caret_token, "\n", output)
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
