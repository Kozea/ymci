from setuptools import setup, find_packages

setup(
    name='ymci-ext-oauth',
    version='1.2',
    description='OAuth plugin for ymci',
    author='Florian Mounier, Kozea',
    author_email='florian.mounier@kozea.fr',

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_oauth'],
    packages=find_packages(),
    package_data={'ymci_ext_oauth': ['templates/*', 'static/*']},

    entry_points={
        'ymci.ext': [
            'ymci-ext-oauth = ymci_ext_oauth'
        ],
        'ymci.ext.db.Table': [
            'oauth_table = ymci_ext_oauth.db:OAuthProjectConfig'
        ],
        'ymci.ext.form.Form': [
            'form = ymci_ext_oauth.form:OAuthConfigForm'
        ],
        'ymci.ext.routes.Route': [
            'result_chart = ymci_ext_oauth.routes:GoogleOAuth2LoginHandler'
        ],
        'ymci.ext.hooks.PrepareHook': [
            'oauth_hook = ymci_ext_oauth.hooks:OAuthHook'
        ]
    }
)
