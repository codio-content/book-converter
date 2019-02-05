import unittest
import os

from converter.latex2markdown import LaTeX2Markdown
from converter.guides.tools import write_file


def write_md_case(name, content):
    dn = os.path.dirname(os.path.realpath(__file__))
    fn = os.path.join(dn, 'cases/{}.md'.format(name))
    write_file(fn, content)


def load_tex(path):
    return load_file('{}.tex'.format(path))


def load_md(path):
    return load_file('{}.md'.format(path)).rstrip('\n')


def load_file(path):
    dn = os.path.dirname(os.path.realpath(__file__))
    fn = os.path.join(dn, path)
    with open(fn, 'r') as file:
        return file.read()


class TestSuite(unittest.TestCase):
    def write_md(self, name, refs={}, chapter_num=1):
        path = "cases/{}".format(name)
        converter = LaTeX2Markdown(load_tex(path), refs=refs, chapter_num=chapter_num)
        write_md_case(name, converter.to_markdown())

    def run_case(self, name, refs={}, chapter_num=1):
        path = "cases/{}".format(name)
        converter = LaTeX2Markdown(load_tex(path), refs=refs, chapter_num=chapter_num)
        self.assertEqual(converter.to_markdown(), load_md(path))

    def test_markdown_chapter_render(self):
        self.run_case("chapter")

    def test_markdown_section_render(self):
        self.run_case("section")

    def test_markdown_it_bracket(self):
        self.run_case("it_bracket")

    def test_markdown_em_bracket(self):
        self.run_case("em_bracket")

    def test_markdown_sf_bracket(self):
        self.run_case("sf_bracket")

    def test_markdown_bf_bracket(self):
        self.run_case("bf_bracket")

    def test_markdown_tt_bracket(self):
        self.run_case("tt_bracket")

    def test_markdown_itemize_bracket(self):
        self.run_case("itemize")

    def test_markdown_double_quotes(self):
        self.run_case("double_quotes")

    def test_markdown_url(self):
        self.run_case("url")

    def test_markdown_description(self):
        self.run_case("description")

    def test_markdown_space(self):
        self.run_case("space")

    def test_markdown_comments_simple(self):
        self.run_case("comments_simple")

    def test_markdown_href_simple(self):
        self.run_case("href_simple")

    def test_markdown_href(self):
        self.run_case("href")

    def test_markdown_figure(self):
        self.run_case("figure")

    def test_markdown_trinket(self):
        self.run_case("trinket")

    def test_markdown_stdout(self):
        self.run_case("stdout")

    def test_markdown_code(self):
        self.run_case("code")

    def test_markdown_java(self):
        self.run_case("java")

    def test_markdown_verb(self):
        self.run_case("verb")

    def test_markdown_table(self):
        self.run_case("table")

    def test_markdown_enumerate(self):
        self.run_case("enumerate")

    def test_markdown_small(self):
        self.run_case("small")

    def test_markdown_exercise(self):
        self.run_case("exercise")

    def test_markdown_quote(self):
        self.run_case("quote")

    def test_markdown_quotation(self):
        self.run_case("quotation")

    def test_markdown_tabular(self):
        self.run_case("tabular")

    def test_markdown_textbf(self):
        self.run_case("textbf")

    def test_markdown_stress(self):
        self.run_case("stress")

    def test_markdown_ref(self):
        refs = {}
        refs['javadoc'] = {
            'chapter': 'javadoc',
            'section': 'javadoc',
            'counter': '2.2'
        }
        self.run_case("ref", refs=refs)

    def test_markdown_pageref(self):
        refs = {}
        refs['code'] = {
            'chapter': 'code',
            'section': 'code',
            'counter': '2.2'
        }
        self.run_case("pageref", refs=refs)
