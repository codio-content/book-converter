import logging
import glob
import shutil

from pathlib import Path


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


def _convert_assets(config, generate_dir, pdfs_for_convert, convert_from_path):
    base_src_dir = Path(config['workspace']['directory'])
    for pdf in pdfs_for_convert:
        logging.debug("convert %s to jpg" % pdf)
        pdf_file = base_src_dir.joinpath(pdf)
        pages = convert_from_path(pdf_file, 500)

        dst_folder = Path(generate_dir).joinpath(Path(pdf).parent)
        dst_folder.mkdir(exist_ok=True, parents=True)

        if pages:
            image = Path(pdf.replace('.pdf', '.jpg'))
            page = pages[0]
            page.save(dst_folder.joinpath(image.name), 'JPEG')


def convert_assets(config, generate_dir, pdfs_for_convert):
    try:
        from pdf2image import convert_from_path
        _convert_assets(config, generate_dir, pdfs_for_convert, convert_from_path)
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
