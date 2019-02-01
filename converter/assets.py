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

    dst.mkdir()

    for file in glob.glob(str(src.joinpath(value))):
        shutil.copy(file, dst.joinpath(Path(file).name))


def copy_assets(config, generate_dir):
    assets = config.get('assets')
    if assets:
        base_src_dir = Path(config['workspace']['directory'])
        for asset in assets:
            if isinstance(asset, str):
                copy_tree(asset, base_src_dir, generate_dir)
            elif isinstance(asset, dict):
                copy_globing(asset, base_src_dir, generate_dir)
