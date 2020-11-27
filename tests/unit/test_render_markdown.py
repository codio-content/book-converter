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
    with open(fn, 'r', encoding='utf-8') as file:
        return file.read()


def make_converter(path, refs, chapter_num, load_workspace_file):
    return LaTeX2Markdown(
        load_tex(path).split('\n'), refs=refs, chapter_num=chapter_num, detect_asset_ext=lambda _: "png",
        load_workspace_file=load_workspace_file
    )


class TestSuite(unittest.TestCase):

    maxDiff = None

    def write_md(self, name, refs={}, chapter_num=1, load_workspace_file=lambda _: _):
        path = "cases/{}".format(name)
        converter = make_converter(path, refs, chapter_num, load_workspace_file)
        write_md_case(name, converter.to_markdown())

    def run_case(self, name, refs={}, chapter_num=1, load_workspace_file=lambda _: _):
        path = "cases/{}".format(name)
        converter = make_converter(path, refs, chapter_num, load_workspace_file)
        self.assertEqual(load_md(path), converter.to_markdown().rstrip('\n'))

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
        self.run_case("space_both")

    def test_markdown_comments_simple(self):
        self.run_case("comments_simple")

    def test_markdown_comments(self):
        self.run_case("comments")

    def test_markdown_href_simple(self):
        self.run_case("href_simple")

    def test_markdown_href(self):
        self.run_case("href")

    def test_markdown_figure(self):
        self.run_case("figure")

    def test_markdown_figure_complex(self):
        self.run_case("figure_complex")

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
            'pageref': 'javadoc',
            'ref': '2.2'
        }
        self.run_case("ref", refs=refs)

    def test_markdown_pageref(self):
        refs = {}
        refs['code'] = {
            'pageref': 'code'
        }
        refs['page'] = {
            'pageref': 100
        }
        self.run_case("pageref", refs=refs)
        self.run_case("pageref_num", refs=refs)

    def test_math(self):
        self.run_case("math")

    def test_eqnarray(self):
        self.run_case("eqnarray")

    def test_new_line(self):
        self.run_case("new_line")

    def test_esc_code(self):
        self.run_case("esc_code")

    def test_verbatim(self):
        self.run_case("verbatim")

    def test_redis(self):
        self.run_case("redis")

    def test_math_runtime(self):
        self.run_case("math_runtime")

    def test_w_directive(self):
        self.run_case("w")

    def test_x_directive(self):
        self.run_case("x")

    def test_t_directive(self):
        self.run_case("T")

    def test_emph_directive(self):
        self.run_case("emph")

    def test_ldots_directive(self):
        self.run_case("ldots")

    def test_sidebargraphic(self):
        self.run_case("sidebargraphic")

    def test_makequotation(self):
        self.run_case("makequotation")

    def test_weblink(self):
        self.run_case("weblink")

    def test_tbd(self):
        self.run_case("tbd")

    def test_sidebar(self):
        self.run_case("sidebar")

    def test_saas_icons(self):
        self.run_case("saas_icons")

    def test_bc(self):
        self.run_case("bc")

    def test_picfigure(self):
        self.run_case("picfigure")

    def test_summary(self):
        self.run_case("summary")

    def test_checkyourself(self):
        self.run_case("checkyourself")

    def test_cite(self):
        self.run_case("cite")

    def test_center(self):
        self.run_case("center")

    def test_concepts(self):
        self.run_case("concepts")

    def test_elaboration(self):
        self.run_case("elaboration")

    def test_pitfall(self):
        self.run_case("pitfall")

    def test_fallacy(self):
        self.run_case("fallacy")

    def test_saas(self):
        self.run_case("saas", load_workspace_file=lambda _: "file content")
        self.run_case("saas1")
        self.run_case("saas2")
        self.run_case("saas3")

    def test_italic_bold(self):
        self.run_case("italic_bold")

    def test_esc_dollar(self):
        self.run_case("esc_dol")

    def test_index(self):
        self.run_case("index")

    def test_ifhtmloutput(self):
        self.run_case("ifhtmloutput")

    def test_tablefigure(self):
        self.run_case("tablefigure", load_workspace_file=lambda _: "file content\n content")

    def test_chips(self):
        self.run_case("chips")

    def test_dedicationwithpic(self):
        self.run_case("dedicationwithpic")

    def test_tolearnmore(self):
        self.run_case("tolearnmore")

    def test_codefigure(self):
        self.run_case("codefigure", load_workspace_file=lambda _: "file content")

    def test_codefile(self):
        self.run_case("codefile", load_workspace_file=lambda _: "file content")

    def test_checkyourself_complex(self):
        self.run_case("checkyourself_complex")

    def test_screencast(self):
        self.run_case("screencast")

    def test_html(self):
        self.run_case("html")

    def test_nested_list(self):
        self.run_case("nested_list")

    def test_tabularx(self):
        self.run_case("tabularx")

    def test_twoicons(self):
        self.run_case("twoicons")

    def test_turingwinner(self):
        self.run_case("turingwinner")

    def test_equation(self):
        self.run_case("equation")
