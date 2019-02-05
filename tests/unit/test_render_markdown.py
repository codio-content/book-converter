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

    def test_chapter_render(self):
        self.run_case("chapter")

    def test_section_render(self):
        self.run_case("section")

    def test_it_bracket(self):
        self.run_case("it_bracket")

    def test_em_bracket(self):
        self.run_case("em_bracket")

    def test_sf_bracket(self):
        self.run_case("sf_bracket")

    def test_bf_bracket(self):
        self.run_case("bf_bracket")

    def test_tt_bracket(self):
        self.run_case("tt_bracket")

    def test_itemize_bracket(self):
        self.run_case("itemize")

    def test_double_quotes(self):
        self.run_case("double_quotes")

    def test_url(self):
        self.run_case("url")

    def test_description(self):
        self.run_case("description")

    def test_space(self):
        self.run_case("space")

    def test_comments_simple(self):
        self.run_case("comments_simple")

    def test_href_simple(self):
        self.run_case("href_simple")

    def test_href(self):
        self.run_case("href")

    def test_figure(self):
        self.run_case("figure")

    def test_trinket(self):
        self.run_case("trinket")

    def test_stdout(self):
        self.run_case("stdout")

    def test_code(self):
        self.run_case("code")

    def test_java(self):
        self.run_case("java")

    def test_verb(self):
        self.run_case("verb")

    def test_table(self):
        self.run_case("table")

    def test_enumerate(self):
        self.run_case("enumerate")

    def test_small(self):
        self.run_case("small")

    def test_exercise(self):
        self.run_case("exercise")

    def test_quote(self):
        self.run_case("quote")

    def test_quotation(self):
        self.run_case("quotation")

    def test_tabular(self):
        self.run_case("tabular")

    def test_textbf(self):
        self.run_case("textbf")

    def test_stress(self):
        self.run_case("stress")

    def test_ref(self):
        refs = {}
        refs['javadoc'] = {
            'chapter': 'javadoc',
            'section': 'javadoc',
            'counter': '2.2'
        }
        self.run_case("ref", refs=refs)

    def test_pageref(self):
        refs = {}
        refs['code'] = {
            'chapter': 'code',
            'section': 'code',
            'counter': '2.2'
        }
        self.run_case("pageref", refs=refs)
