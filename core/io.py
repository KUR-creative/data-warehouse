from pathlib import Path

import yaml


def dump_data_yaml(out_path, dic):
    Path(out_path).write_text(
        yaml.dump(dic, allow_unicode=True, sort_keys=False))
