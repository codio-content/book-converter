import logging
import subprocess

from argparse import ArgumentParser
from os import listdir
from pathlib import Path
from collections import namedtuple

from converter.weteach2markdown import normalize_output

DocumentsToProcess = namedtuple('DocumentsToProcess', ['base_dir', 'name', 'doc'])


def sort_processing_items_key(item):
    """
    Topic_1.1
    Topic_1.2
    ...
    Unit_1_Project
    Topic_2.1
    Topic_2.2
    ...
    Unit_2_Project
    ....
    Unit_N_Project
    """
    parts = item.name.split('_')
    sub_num = int(float(parts[1]) * 1000)
    if item.name.startswith('Unit'):
        sub_num += 999
    sub_pre = parts[-1]
    if sub_pre.isalpha():
        return f'{sub_num}{sub_pre}'
    return f'{sub_num}'


def sort_processing_items(items):
    return sorted(items, key=sort_processing_items_key)


def convert(base_directory, output):
    print('output', output)
    to_process = []
    for f_item in listdir(base_directory):
        sub_content = base_directory.joinpath(f_item)
        if sub_content.is_dir():
            for file in Path(sub_content).rglob('*.docx'):
                if not file.name.startswith('~'):
                    to_process.append(DocumentsToProcess(sub_content, f_item, file))

    sorted_items = sort_processing_items(to_process)
    convert_docx(sorted_items[4], output)


def convert_docx(element, output_dir):
    media_dir = output_dir.joinpath('.guides').absolute()
    command = ['pandoc', '--extract-media', str(media_dir), '--wrap=none', '-t', 'markdown', element.doc]
    result = subprocess.run(command, capture_output=True)
    utf8_output = result.stdout.decode('utf-8')
    normalized_output = normalize_output(utf8_output, str(output_dir))
    print('normalized_output', normalized_output)


def main():
    parser = ArgumentParser(description='Process weteach-cs docs to codio guides.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+', help='path to a sources directory')
    parser.add_argument('-l', '--log', action='store', default=None)
    parser.add_argument('--output', type=str, help='path to output folder')

    args = parser.parse_args()

    logging.basicConfig(filename=args.log, level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname).5s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')

    for path in args.paths:
        convert(Path(path), Path(args.output))


if __name__ == '__main__':
    main()