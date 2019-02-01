import yaml
import logging

from pathlib import Path


def load_config_file(base_path):
    base_path = Path(base_path)
    file_path = base_path
    if base_path.is_dir():
        file_path = base_path.joinpath("codio_structure.yml")
        if not file_path.is_file():
            file_path = base_path.joinpath("codio_structure.yaml")
        if not file_path.is_file():
            raise BaseException("Structure not found")
    with open(file_path, 'r') as stream:
        try:
            return yaml.load(stream), file_path.parent
        except yaml.YAMLError as exc:
            logging.error("load config file exception", exc)
            raise BaseException("load config file exception")
