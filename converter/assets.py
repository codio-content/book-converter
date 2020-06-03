import logging
import glob
import shutil
from os import listdir

from pathlib import Path

from converter.guides.tools import write_file


def copy_tree(asset, base_src_dir, generate_dir):
    src = base_src_dir.joinpath(asset)
    dst = generate_dir.joinpath(asset)
    shutil.copytree(src, dst)


def copy_globing(asset, base_src_dir, generate_dir):
    key = next(iter(asset))
    value = asset[key]

    src = base_src_dir.joinpath(key)
    dst = generate_dir.joinpath(key)

    dst.mkdir(exist_ok=True, parents=True)

    for file in glob.glob(str(src.joinpath(value))):
        shutil.copy(file, dst.joinpath(Path(file).name))

    for file in glob.glob(str(src.joinpath('**/{}'.format(value)))):
        name = str(file).replace(str(src), '').lstrip('/')
        file_path = dst.joinpath(name)
        file_path.parent.mkdir(exist_ok=True, parents=True)
        shutil.copy(file, file_path)


def _convert_assets(config, generate_dir, pdfs_for_convert, convert_from_path, bookdown=False):
    base_src_dir = Path(config['workspace']['directory'])
    for pdf in set(pdfs_for_convert):
        logging.debug("convert %s to jpg" % pdf)
        pdf_file = base_src_dir.joinpath('_bookdown_files').joinpath(pdf) if bookdown else base_src_dir.joinpath(pdf)
        if not pdf_file.exists():
            pdf = '{}.pdf'.format(pdf)
            pdf_file = base_src_dir.joinpath('_bookdown_files').joinpath(pdf)\
                if bookdown else base_src_dir.joinpath(pdf)
            if not pdf_file.exists():
                continue

        dst_folder = Path(generate_dir).joinpath(Path(pdf).parent)
        dst_folder.mkdir(exist_ok=True, parents=True)

        try:
            pages = convert_from_path(pdf_file, 300)
            if pages:
                image = Path(pdf.replace('.pdf', '.jpg'))
                page = pages[0]
                page.save(dst_folder.joinpath(image.name), 'JPEG')
        except KeyboardInterrupt as e:
            raise e
        except BaseException as e:
            logging.error("convert %s to jpg error" % pdf)
            logging.error(e)


def convert_assets(config, generate_dir, pdfs_for_convert, bookdown=False):
    try:
        from pdf2image import convert_from_path
        _convert_assets(config, generate_dir, pdfs_for_convert, convert_from_path, bookdown=bookdown)
    except Exception as e:
        logging.error("pdf2image is not installed", e)


def copy_assets(config, generate_dir):
    assets = config.get('assets')
    if assets:
        base_src_dir = Path(config['workspace']['directory'])
        for asset in assets:
            try:
                if isinstance(asset, str):
                    copy_tree(asset, base_src_dir, generate_dir)
                elif isinstance(asset, dict):
                    copy_globing(asset, base_src_dir, generate_dir)
            except BaseException as e:
                logging.exception("can not copy asset {}".format(asset))


def process_source_code(source_codes, generate_dir, use_code_folder=True):
    code_dir = generate_dir.joinpath('code') if use_code_folder else generate_dir
    counter = {}
    for code in source_codes:
        current = counter.setdefault(code.name, 0)
        source_dir = code_dir
        if current:
            source_dir = source_dir.joinpath(str(current))
        source_dir.mkdir(exist_ok=True, parents=True)
        file_path = source_dir.joinpath(code.name)
        file_path.parent.mkdir(exist_ok=True, parents=True)
        if file_path.exists():
            current += 1
            source_dir = source_dir.joinpath(str(current))
            file_path = source_dir.joinpath(code.name)
        logging.info("write {} to {}".format(code.name, file_path))
        write_file(file_path, code.source)
        counter[code.name] = current + 1


def copy_files_from_bookdown_folder(config, generate_dir):
    base_src_dir = Path(config['workspace']['directory'])
    bookdown_dir = base_src_dir.joinpath('_bookdown_files')
    for f_item in listdir(base_src_dir.joinpath('_bookdown_files')):
        copy_globing({f_item: '*.png'}, bookdown_dir, generate_dir)
        copy_globing({f_item: '*.jpg'}, bookdown_dir, generate_dir)
