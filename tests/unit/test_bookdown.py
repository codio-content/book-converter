import unittest
import os

from converter.bookdown2markdown import BookDown2Markdown


def load_book_md(path):
    return load_file('{}.bookdown.md'.format(path)).rstrip('\n')


def load_md(path):
    return load_file('{}.md'.format(path)).rstrip('\n')


def load_file(path):
    dn = os.path.dirname(os.path.realpath(__file__))
    fn = os.path.join(dn, path)
    with open(fn, 'r', encoding="utf-8") as file:
        return file.read()


class TestSuite(unittest.TestCase):
    def run_case(self, name, refs={}):
        path = "bookdown_cases/{}".format(name)
        converter = BookDown2Markdown(load_book_md(path).split('\n'), assets_extension=lambda x: "jpg", refs=refs)
        self.assertEqual(converter.to_markdown(), load_md(path))

    def test_bookdown_includegraphics(self):
        self.run_case("includegraphics")

    def test_bookdown_refs(self):
        refs = {
            "data visualisation": {
                "ref": "Data Visualisation Chapter"
            },
            "wrangle": {
                "ref": "Wrangle Chapter"
            },
            "fig:tidy-structure": {
                "ref": "Tidy Structure"
            }
        }
        self.run_case("refs", refs)
