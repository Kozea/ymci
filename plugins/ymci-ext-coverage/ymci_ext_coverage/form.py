from ymci.ext.form import Form
from .db import CoverageConfig


class CoverageForm(Form):
    class Meta(object):
        model = CoverageConfig
        only = CoverageConfig.columns_list
