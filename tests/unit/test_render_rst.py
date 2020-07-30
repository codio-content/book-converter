import unittest
import os

from converter.rst2markdown import Rst2Markdown
from converter.guides.tools import write_file


def write_md_case(name, content):
    dn = os.path.dirname(os.path.realpath(__file__))
    fn = os.path.join(dn, 'cases_rst/{}.md'.format(name))
    write_file(fn, content)


def load_file(path):
    dn = os.path.dirname(os.path.realpath(__file__))
    fn = os.path.join(dn, path)
    with open(fn, 'r') as file:
        return file.read()


def load_rst(path):
    return load_file('{}.rst'.format(path))


def load_md(path):
    return load_file('{}.md'.format(path)).rstrip('\n')


def make_converter(path):
    return Rst2Markdown(load_rst(path).split('\n'))


class TestSuite(unittest.TestCase):
    def write_md(self, name):
        path = "cases_rst/{}".format(name)
        converter = make_converter(path)
        write_md_case(name, converter.to_markdown())

    def run_case(self, name):
        path = "cases_rst/{}".format(name)
        converter = make_converter(path)
        self.assertEqual(load_md(path), converter.to_markdown().rstrip('\n'))

    def test_markdown_chapter_render(self):
        self.run_case("avembed")
