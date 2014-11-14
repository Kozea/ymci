from ymci.ext.form import Form
from .db import OAuthProjectConfig


class OAuthConfigForm(Form):
    class Meta(object):
        model = OAuthProjectConfig
        only = OAuthProjectConfig.columns_list
