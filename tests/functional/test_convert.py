import unittest
import tempfile
import json

from pathlib import Path

from converter.loader import load_config_file
from converter.convert import convert


def get_file_path(name='', extension='tex'):
    dn = Path(__file__).resolve().parent
    if not name:
        return dn.joinpath('cases')
    return dn.joinpath('cases/{}.{}'.format(name, extension))


def load_file(path):
    with open(path, 'r') as file:
        return file.read().strip('\n')


class TestSuite(unittest.TestCase):
    def test_convert(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            check_exists = [
                'code/GuessSoln.java',
                '.guides/book.json',
                '.guides/metadata.json',
                '.guides/content/computer-programming.md',
                '.guides/content/computer-programming-what-is-a-computer-.md',
                '.guides/content/computer-programming-what-is-programming-.md',
                '.guides/content/variables-and-operators.md',
                '.guides/content/variables-and-operators-assigning-variables.md',
                '.guides/content/variables-and-operators-declaring-variables.md'
            ]

            for path in check_exists:
                check = generate.joinpath(path)
                self.assertTrue(check.exists())

            check_content = [
                (
                    '.guides/content/computer-programming.md',
                    '##  Computer programming\n\n\nComputer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    '###  What is a computer?\n\n\nWhat is a computer? content'
                ),
                (
                    '.guides/content/computer-programming-what-is-programming-.md',
                    '###  What is programming?\n\n\nWhat is programming? content'
                ),
                (
                    '.guides/content/variables-and-operators.md',
                    '##  Variables and operators\n\n\nVariables and operators content'
                ),
                (
                    '.guides/content/variables-and-operators-assigning-variables.md',
                    '###  Assigning variables\n\n\nAssigning variables content'
                ),
                (
                    '.guides/content/variables-and-operators-declaring-variables.md',
                    '###  Declaring variables\n\n\nDeclaring variables content'
                )
            ]

            for path, content in check_content:
                file_content = load_file(generate.joinpath(path))
                self.assertEqual(content, file_content)

            book_raw = load_file(generate.joinpath('.guides/book.json'))
            book = json.loads(book_raw)

            children = book.get('children')
            self.assertEqual(len(children), 2)

            cp = children[0]

            self.assertEqual(cp.get('id'), 'computer-programming')
            self.assertEqual(cp.get('pageId'), 'computer-programming')
            self.assertEqual(cp.get('type'), 'chapter')
            self.assertEqual(cp.get('title'), 'Computer programming')

            cp_children = cp.get('children')

            self.assertEqual(len(cp_children), 2)

            wp = cp_children[1]

            self.assertEqual(wp.get('id'), 'computer-programming-what-is-programming-')
            self.assertEqual(wp.get('pageId'), 'computer-programming-what-is-programming-')
            self.assertEqual(wp.get('type'), 'page')
            self.assertEqual(wp.get('title'), 'What is programming?')

            metadata_raw = load_file(generate.joinpath('.guides/metadata.json'))
            metadata = json.loads(metadata_raw)

            check_sections = {
                'computer-programming': {
                    'content-file': '.guides/content/computer-programming.md',
                    'id': 'computer-programming', 'layout': '2-panels', 'title': 'Computer programming'
                },
                'computer-programming-what-is-a-computer-': {
                    'content-file': '.guides/content/computer-programming-what-is-a-computer-.md',
                    'id': 'computer-programming-what-is-a-computer-', 'title': 'What is a computer?'
                },
                'computer-programming-what-is-programming-': {
                    'content-file': '.guides/content/computer-programming-what-is-programming-.md',
                    'id': 'computer-programming-what-is-programming-', 'title': 'What is programming?'
                },
                'variables-and-operators': {
                    'content-file': '.guides/content/variables-and-operators.md',
                    'id': 'variables-and-operators', 'title': 'Variables and operators'
                },
                'variables-and-operators-declaring-variables': {
                    'content-file': '.guides/content/variables-and-operators-declaring-variables.md',
                    'id': 'variables-and-operators-declaring-variables', 'title': 'Declaring variables'
                },
                'variables-and-operators-assigning-variables': {
                    'content-file': '.guides/content/variables-and-operators-assigning-variables.md',
                    'id': 'variables-and-operators-assigning-variables', 'title': 'Assigning variables'
                }
            }

        sections = metadata.get('sections')

        for section in sections:
            verify = check_sections.get(section.get('id'), {})
            self.assertEqual(section.get('id'), verify.get('id'))
            self.assertEqual(section.get('content-file'), verify.get('content-file'))
            self.assertEqual(section.get('title'), verify.get('title'))
            self.assertEqual(section.get('layout'), verify.get('layout'))

    def test_convert_assets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc1', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            check_exists = [
                'figs/CPU.jpg',
                'figs/meld.png',
                'code/GuessSoln.java',
                '.guides/book.json',
                '.guides/metadata.json',
                '.guides/content/computer-programming.md',
                '.guides/content/computer-programming-what-is-a-computer-.md',
                '.guides/content/computer-programming-what-is-programming-.md',
                '.guides/content/variables-and-operators.md',
                '.guides/content/variables-and-operators-assigning-variables.md',
                '.guides/content/variables-and-operators-declaring-variables.md'
            ]

            for path in check_exists:
                check = generate.joinpath(path)
                self.assertTrue(check.exists())

            check_not_exists = [
                'figs/aliasing.pdf',
                'figs/circle.fig'
            ]

            for path in check_not_exists:
                check = generate.joinpath(path)
                self.assertFalse(check.exists())

    def test_convert_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc2', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            metadata_raw = load_file(generate.joinpath('.guides/metadata.json'))
            metadata = json.loads(metadata_raw)

            self.assertTrue(metadata.get('hideMenu'))
            self.assertTrue(metadata.get('protectLayout'))

    def test_convert_configuration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc3', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            metadata_raw = load_file(generate.joinpath('.guides/metadata.json'))
            metadata = json.loads(metadata_raw)

            sections = metadata.get('sections')

            section = sections[0]
            self.assertEqual(section.get('layout'), '2-panels-tree')
            self.assertEqual(len(section.get('files')), 1)

    def test_convert_transformations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc4', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            check_content = [
                (
                    '.guides/content/computer-programming.md',
                    '##  Computer programming\n\nMy simple text\n\nComputer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    '###  What is a computer?\n\n\nWhat is a computer? content'
                ),
                (
                    '.guides/content/computer-programming-what-is-programming-.md',
                    '###  What is programming?'
                ),
                (
                    '.guides/content/variables-and-operators.md',
                    '##  Variables and operators\n\n\nVariables and operators content'
                ),
                (
                    '.guides/content/variables-and-operators-assigning-variables.md',
                    '###  Assigning variables\n\n\nAssigning variables content'
                ),
                (
                    '.guides/content/variables-and-operators-declaring-variables.md',
                    '###  Declaring variables\n\n\nDeclaring variables content'
                )
            ]

            for path, content in check_content:
                file_content = load_file(generate.joinpath(path))
                self.assertEqual(content, file_content)
