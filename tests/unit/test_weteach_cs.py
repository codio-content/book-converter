import unittest
import os

from converter.guides.tools import write_file
from converter.weteach2markdown import normalize_output


def write_md_case(name, content):
    dn = os.path.dirname(os.path.realpath(__file__))
    fn = os.path.join(dn, 'weteach_cases/{}_out.md'.format(name))
    write_file(fn, content)


def load_file(path):
    dn = os.path.dirname(os.path.realpath(__file__))
    fn = os.path.join(dn, path)
    with open(fn, 'r') as file:
        return file.read()


def load_in(path):
    return load_file('{}_in.md'.format(path))


def load_out(path):
    return load_file('{}_out.md'.format(path)).rstrip('\n')


class TestSuite(unittest.TestCase):
    def write_md(self, name):
        path = "weteach_cases/{}".format(name)
        unit_name, topic_name, content = normalize_output(load_in(path), 'media1')
        write_md_case(name, content)

    def run_case(self, name):
        path = "weteach_cases/{}".format(name)
        unit_name, topic_name, content = normalize_output(load_in(path), 'media1')
        self.assertEqual(load_out(path), content)
        return unit_name, topic_name, content

    def test_render1(self):
        self.run_case("render1")
