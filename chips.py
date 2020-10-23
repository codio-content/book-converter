import logging
from argparse import ArgumentParser

from converter.chips.chips_convert import convert_chips_doc, generate_chips_toc
from converter.loader import load_config_file

if __name__ == '__main__':
    parser = ArgumentParser(description='Process convert assesment doc to codio guides')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+', help='target path')
    parser.add_argument('--generate', type=str, help='path to readme file')
    parser.add_argument('-l', '--log', action='store', default=None)
    parser.add_argument('-y', '--yes', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(filename=args.log, level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname).5s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')

    logging.getLogger('PIL').setLevel(logging.WARN)

    if args.generate:
        generate_chips_toc(args.paths[0], args.generate)
    else:
        config, base_path = load_config_file(args.paths[0])
        convert_chips_doc(config, base_path, args.yes)
