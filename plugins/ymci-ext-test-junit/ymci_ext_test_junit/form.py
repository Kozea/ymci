from ymci.ext.form import Form
from .db import JUnitConfig


class JUnitForm(Form):
    class Meta(object):
        model = JUnitConfig
        only = JUnitConfig.columns_list
