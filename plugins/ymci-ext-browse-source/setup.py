from setuptools import setup, find_packages

setup(
    name='ymci-ext-browse-source',
    version='1.0',
    description='Source browser plugin for ymci',
    author="Florian Mounier, Kozea",
    author_email="florian.mounier@kozea.fr",

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_browse_source'],
    packages=find_packages(),
    install_requires=['pygments'],
    package_data={'ymci': ['templates/*']},
    entry_points={
        'ymci.ext.routes.Route': [
            'browse = ymci_ext_browse_source.routes:Browse'
        ],
    }
)
