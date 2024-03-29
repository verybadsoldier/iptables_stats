import yaml


def load_config(filepath):
    with open(filepath, 'r') as stream:
        return yaml.safe_load(stream)
