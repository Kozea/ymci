# -*- coding: utf-8 -*-
#
# ymci - You Modern Continous Integration server
# Copyright © 2014 Florian Mounier, Kozea

import os
import yaml


class Config(object):

    def __init__(self, path):
        self._config = {
            'projects_path': 'projects'
        }
        self._read(path)
        self._sync()

    def _read(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self._config.update(yaml.load(f))
        self._config['path'] = path

    def _sync(self):
        with open(self._config['path'], 'w') as f:
            f.write(yaml.safe_dump(
                self._config, default_flow_style=False, allow_unicode=True))

    def __getitem__(self, item):
        return self._config.__getitem__(item)

    def __setitem__(self, item, val):
        return self._config.__setitem__(item, val)
