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
                    'Computer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    'What is a computer? content'
                ),
                (
                    '.guides/content/computer-programming-what-is-programming-.md',
                    'What is programming? content'
                ),
                (
                    '.guides/content/variables-and-operators.md',
                    'Variables and operators content'
                ),
                (
                    '.guides/content/variables-and-operators-assigning-variables.md',
                    'Assigning variables content'
                ),
                (
                    '.guides/content/variables-and-operators-declaring-variables.md',
                    'Declaring variables content'
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
                    'My simple text\n\nComputer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    'What is a computer? content'
                ),
                (
                    '.guides/content/computer-programming-what-is-programming-.md',
                    ''
                ),
                (
                    '.guides/content/variables-and-operators.md',
                    'Variables and operators content'
                ),
                (
                    '.guides/content/variables-and-operators-assigning-variables.md',
                    'Assigning variables content'
                ),
                (
                    '.guides/content/variables-and-operators-declaring-variables.md',
                    'Declaring variables content'
                )
            ]

            for path, content in check_content:
                file_content = load_file(generate.joinpath(path))
                self.assertEqual(content, file_content)

    def test_refs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc_ref', extension='yml'))
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
                    'Computer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    'What is a computer? content'
                ),
                (
                    '.guides/content/computer-programming-what-is-programming-.md',
                    'What is programming? content\n\n1 in section Declaring variables'
                ),
                (
                    '.guides/content/variables-and-operators.md',
                    'Variables and operators content'
                ),
                (
                    '.guides/content/variables-and-operators-assigning-variables.md',
                    'Assigning variables content\n\n1.1 in section Assigning variables'
                ),
                (
                    '.guides/content/variables-and-operators-declaring-variables.md',
                    'Declaring variables content'
                )
            ]

            for path, content in check_content:
                file_content = load_file(generate.joinpath(path))
                self.assertEqual(content, file_content)

    def test_refs_0(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc_ref_0', extension='yml'))
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
                    'Computer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    'What is a computer? content'
                ),
                (
                    '.guides/content/computer-programming-what-is-programming-.md',
                    'What is programming? content\n\n0 in section Declaring variables'
                ),
                (
                    '.guides/content/variables-and-operators.md',
                    'Variables and operators content'
                ),
                (
                    '.guides/content/variables-and-operators-assigning-variables.md',
                    'Assigning variables content\n\n0.1 in section Assigning variables'
                ),
                (
                    '.guides/content/variables-and-operators-declaring-variables.md',
                    'Declaring variables content'
                )
            ]

            for path, content in check_content:
                file_content = load_file(generate.joinpath(path))
                self.assertEqual(content, file_content)

    def test_refs_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc_ref_override', extension='yml'))
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
                    'Computer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    'What is a computer? content'
                ),
                (
                    '.guides/content/computer-programming-what-is-programming-.md',
                    'What is programming? content\n\noverride.1 100'
                ),
                (
                    '.guides/content/variables-and-operators.md',
                    'Variables and operators content'
                ),
                (
                    '.guides/content/variables-and-operators-assigning-variables.md',
                    'Assigning variables content\n\n1.1 in section override.3'
                ),
                (
                    '.guides/content/variables-and-operators-declaring-variables.md',
                    'Declaring variables content'
                )
            ]

            for path, content in check_content:
                file_content = load_file(generate.joinpath(path))
                self.assertEqual(content, file_content)

    def test_skip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc5', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            check_exists = [
                'code/GuessSoln.java',
                '.guides/book.json',
                '.guides/metadata.json',
                '.guides/content/computer-programming.md',
                '.guides/content/computer-programming-what-is-programming-.md',
                '.guides/content/variables-and-operators.md',
                '.guides/content/variables-and-operators-assigning-variables.md',

            ]

            for path in check_exists:
                check = generate.joinpath(path)
                self.assertTrue(check.exists())

            check_not_exists = [
                '.guides/content/variables-and-operators-declaring-variables.md',
                '.guides/content/computer-programming-what-is-a-computer-.md'
            ]

            for path in check_not_exists:
                check = generate.joinpath(path)
                self.assertFalse(check.exists())

            book_raw = load_file(generate.joinpath('.guides/book.json'))
            book = json.loads(book_raw)

            children = book.get('children')
            self.assertEqual(2, len(children))

            cp = children[0]

            self.assertEqual(cp.get('id'), 'computer-programming')
            self.assertEqual(cp.get('pageId'), 'computer-programming')
            self.assertEqual(cp.get('type'), 'chapter')
            self.assertEqual(cp.get('title'), 'Computer programming')

            cp_children = cp.get('children')

            self.assertEqual(1, len(cp_children))

            wp = cp_children[0]

            self.assertEqual(wp.get('id'), 'computer-programming-what-is-programming-')
            self.assertEqual(wp.get('pageId'), 'computer-programming-what-is-programming-')
            self.assertEqual(wp.get('type'), 'page')
            self.assertEqual(wp.get('title'), 'What is programming?')

            metadata_raw = load_file(generate.joinpath('.guides/metadata.json'))
            metadata = json.loads(metadata_raw)

            sections = metadata.get('sections')
            self.assertEqual(4, len(sections))

    def test_insert(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc6', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            check_exists = [
                'code/GuessSoln.java',
                '.guides/book.json',
                '.guides/metadata.json',
                '.guides/content/computer-programming.md',
                '.guides/content/computer-programming-what-is-programming-.md',
                '.guides/content/variables-and-operators.md',
                '.guides/content/variables-and-operators-assigning-variables.md',
                '.guides/content/variables-and-operators-exercises-1-3.md',
                '.guides/content/computer-programming-exercises-1-1.md',
                '.guides/content/computer-programming-exercises-1-2.md'

            ]

            for path in check_exists:
                check = generate.joinpath(path)
                self.assertTrue(check.exists(), check)

            check_not_exists = [
                '.guides/content/variables-and-operators-declaring-variables.md',
                '.guides/content/computer-programming-what-is-a-computer-.md'
            ]

            for path in check_not_exists:
                check = generate.joinpath(path)
                self.assertFalse(check.exists(), check)

            book_raw = load_file(generate.joinpath('.guides/book.json'))
            book = json.loads(book_raw)

            children = book.get('children')
            self.assertEqual(2, len(children))

            cp = children[0]

            self.assertEqual(cp.get('id'), 'computer-programming')
            self.assertEqual(cp.get('pageId'), 'computer-programming')
            self.assertEqual(cp.get('type'), 'chapter')
            self.assertEqual(cp.get('title'), 'Computer programming')

            cp_children = cp.get('children')

            self.assertEqual(3, len(cp_children))

            wp = cp_children[0]

            self.assertEqual(wp.get('id'), 'computer-programming-what-is-programming-')
            self.assertEqual(wp.get('pageId'), 'computer-programming-what-is-programming-')
            self.assertEqual(wp.get('type'), 'page')
            self.assertEqual(wp.get('title'), 'What is programming?')

            metadata_raw = load_file(generate.joinpath('.guides/metadata.json'))
            metadata = json.loads(metadata_raw)

            sections = metadata.get('sections')
            self.assertEqual(7, len(sections))

    def test_codio_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc7', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            check_exists = [
                'code/GuessSoln.java',
                '.guides/book.json',
                '.guides/metadata.json',
                '.guides/content/computer-programming.md',
                '.guides/content/computer-programming-what-is-programming-.md',
                '.guides/content/variables-and-operators.md',
                '.guides/content/variables-and-operators-assigning-variables.md',
                '.guides/content/variables-and-operators-declaring-variables.md',
                '.guides/content/computer-programming-what-is-a-computer-.md'
            ]

            for path in check_exists:
                check = generate.joinpath(path)
                self.assertTrue(check.exists(), check)

            book_raw = load_file(generate.joinpath('.guides/book.json'))
            book = json.loads(book_raw)

            children = book.get('children')
            self.assertEqual(2, len(children))

            cp = children[0]

            self.assertEqual(cp.get('id'), 'computer-programming')
            self.assertEqual(cp.get('pageId'), 'computer-programming')
            self.assertEqual(cp.get('type'), 'chapter')
            self.assertEqual(cp.get('title'), 'Computer programming')

            cp_children = cp.get('children')

            self.assertEqual(1, len(cp_children))

            wp = cp_children[0]['children'][0]

            self.assertEqual(wp.get('id'), 'computer-programming-what-is-programming-')
            self.assertEqual(wp.get('pageId'), 'computer-programming-what-is-programming-')
            self.assertEqual(wp.get('type'), 'page')
            self.assertEqual(wp.get('title'), 'What is programming?')

            metadata_raw = load_file(generate.joinpath('.guides/metadata.json'))
            metadata = json.loads(metadata_raw)

            sections = metadata.get('sections')
            self.assertEqual(6, len(sections))

    def test_trinket(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc_trinket', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            check_exists = [
                'code/GuessSoln.java',
                'code/Hello.java',
                'code/1',
                'code/Hello.java',
                'code/GuessSoln.java',
                '.guides/book.json',
                '.guides/metadata.json',
                '.guides/content/computer-programming.md',
                '.guides/content/computer-programming-what-is-programming-.md',
                '.guides/content/variables-and-operators.md',
                '.guides/content/variables-and-operators-assigning-variables.md',
                '.guides/content/variables-and-operators-declaring-variables.md',
                '.guides/content/computer-programming-what-is-a-computer-.md'
            ]

            for path in check_exists:
                check = generate.joinpath(path)
                self.assertTrue(check.exists(), check)

            check_content = [
                (
                    '.guides/content/computer-programming.md',
                    'Computer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    """What is a computer? content

```code
public class Hello {

    public static void main(String[] args) {
        // generate some simple output
        System.out.println("Hello, World!");
    }
}
```"""
                ),
                (
                    '.guides/content/computer-programming-what-is-programming-.md',
                    'What is programming? content'
                ),
                (
                    '.guides/content/variables-and-operators.md',
                    """Variables and operators content

```code
public class Hello {

    public static void main(String[] args) {
        // generate some simple output
        System.out.println("Hello, World!");
    }
}
```"""
                ),
                (
                    '.guides/content/variables-and-operators-assigning-variables.md',
                    """Assigning variables content

```code
public class Hello {

    public static void main(String[] args) {
        // generate some simple output
        System.out.println("Hello, World!");
    }
}
```"""
                ),
                (
                    '.guides/content/variables-and-operators-declaring-variables.md',
                    'Declaring variables content'
                )
            ]

            for path, content in check_content:
                file_content = load_file(generate.joinpath(path))
                self.assertEqual(content, file_content)

    def test_trinket_remove(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc_trinket_remove', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            check_exists = [
                'code/GuessSoln.java',
                'code/Hello.java',
                'code/1',
                'code/Hello.java',
                'code/GuessSoln.java',
                '.guides/book.json',
                '.guides/metadata.json',
                '.guides/content/computer-programming.md',
                '.guides/content/computer-programming-what-is-programming-.md',
                '.guides/content/variables-and-operators.md',
                '.guides/content/variables-and-operators-assigning-variables.md',
                '.guides/content/variables-and-operators-declaring-variables.md',
                '.guides/content/computer-programming-what-is-a-computer-.md'
            ]

            for path in check_exists:
                check = generate.joinpath(path)
                self.assertTrue(check.exists(), check)

            check_content = [
                (
                    '.guides/content/computer-programming.md',
                    'Computer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    """What is a computer? content"""
                ),
                (
                    '.guides/content/computer-programming-what-is-programming-.md',
                    'What is programming? content'
                ),
                (
                    '.guides/content/variables-and-operators.md',
                    """Variables and operators content"""
                ),
                (
                    '.guides/content/variables-and-operators-assigning-variables.md',
                    """Assigning variables content"""
                ),
                (
                    '.guides/content/variables-and-operators-declaring-variables.md',
                    'Declaring variables content'
                )
            ]

            for path, content in check_content:
                file_content = load_file(generate.joinpath(path))
                self.assertEqual(content, file_content)

    def test_refs_multi(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            generate = tmp.joinpath('generate')
            config, base_path = load_config_file(get_file_path('toc_ref_multi', extension='yml'))
            config['workspace']['directory'] = base_path
            convert(config, tmp, True)

            check_content = [
                (
                    '.guides/content/computer-programming.md',
                    'Computer programming content'
                ),
                (
                    '.guides/content/computer-programming-what-is-a-computer-.md',
                    'What is a computer? content'
                ),
                (
                    '.guides/content/what-is-programming-.md',
                    'What is programming? content\n\n0 in section Declaring variables'
                ),
                (
                    '.guides/content/what-is-programming-variables-and-operators.md',
                    'Variables and operators content 2'
                ),
                (
                    '.guides/content/assigning-variables.md',
                    'Assigning variables content\n\n0.1 in section Assigning variables'
                )
            ]

            for path, content in check_content:
                file_content = load_file(generate.joinpath(path))
                self.assertEqual(content, file_content)
