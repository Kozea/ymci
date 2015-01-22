# -*- coding: utf-8 -*-
#
# ymci - You Modern Continuous Integration server
# Copyright © 2014 Florian Mounier, Kozea

import os
import yaml


class Config(dict):

    def __init__(self, path):
        super().__init__()
        self.update({
            'projects_path': 'projects',
            'db_url': 'postgresql+psycopg2://ymci@localhost/ymci'
        })

        self._read(path)
        self._sync()

    def _read(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.update(yaml.load(f))
        self['path'] = path

    def _sync(self):
        with open(self['path'], 'w') as f:
            f.write(yaml.safe_dump(
                dict(self), default_flow_style=False, allow_unicode=True))
