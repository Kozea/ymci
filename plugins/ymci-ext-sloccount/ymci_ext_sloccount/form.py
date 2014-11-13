from ymci.ext.form import Form
from .db import SloccountConfig


class SloccountForm(Form):
    class Meta(object):
        model = SloccountConfig
        only = SloccountConfig.columns_list
