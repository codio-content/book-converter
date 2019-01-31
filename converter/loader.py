import yaml


def load_config_file(file_path):
    with open(file_path, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print("load config file exception", exc)
