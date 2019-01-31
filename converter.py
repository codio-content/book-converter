from argparse import ArgumentParser
from converter.toc import generate_toc
from converter.loader import load_config_file
from converter.convert import convert

if __name__ == '__main__':
    parser = ArgumentParser(description='Process latex to codio guides.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+', help='path to a book config')
    parser.add_argument('--generate', type=str, help='path to a latex book')

    args = parser.parse_args()
    if args.generate:
        generate_toc(args.paths[0], args.generate)
    else:
        # todo: multi
        config = load_config_file(args.paths[0])
        convert(config)
