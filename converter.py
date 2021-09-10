import logging
from argparse import ArgumentParser

from converter.toc import generate_toc
from converter.loader import load_config_file
from converter.convert import convert, convert_bookdown, convert_rst_json, convert_rst_toctree
from converter.refs import ref_dict

if __name__ == '__main__':
    parser = ArgumentParser(description='Process convert to codio guides.')
    parser.add_argument('paths', metavar='PATH', type=str, nargs='+', help='path to a book config')
    parser.add_argument('--source', type=str, help='path to source')
    parser.add_argument('--generate', type=str, help='path to a latex book')
    parser.add_argument('-l', '--log', action='store', default=None)
    parser.add_argument('-y', '--yes', action='store_true')
    parser.add_argument('-r', '--ref', action='store_true')

    args = parser.parse_args()

    logging.basicConfig(filename=args.log, level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname).5s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')

    logging.getLogger('PIL').setLevel(logging.WARN)

    if args.generate:
        generate_toc(args.paths[0], args.generate, args.source)
    elif args.ref:
        config, base_path = load_config_file(args.paths[0])
        ref_dict(config)
    else:
        for path in args.paths:
            config, base_path = load_config_file(path)
            if config.get('workspace', {}).get('tex'):
                convert(config, base_path, args.yes)
            elif config.get('workspace', {}).get('bookdown'):
                convert_bookdown(config, base_path, args.yes)
            elif config.get('workspace', {}).get('json'):
                convert_rst_json(config, base_path, args.yes)
            elif config.get('workspace', {}).get('rst'):
                convert_rst_toctree(config, base_path, args.yes)

