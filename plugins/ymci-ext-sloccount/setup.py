from setuptools import setup, find_packages

setup(
    name='ymci-ext-sloccount',
    version='1.0',
    description='Sloccount plugin for ymci',
    author="Clément Plasse, Kozea",
    author_email="clement.plasse@kozea.fr",

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_sloccount'],
    packages=find_packages(),

    entry_points={
        'ymci.ext.hooks.BuildHook': [
            'sloccount = ymci_ext_sloccount.sloccount:SloccountHook'
        ],
        'ymci.ext.db.Table': [
            'result = ymci_ext_sloccount.db:Sloccount'
        ],
        'ymci.ext.routes.Route': [
            'result_chart = ymci_ext_sloccount.routes:SloccountChart'
        ],
    }
)
