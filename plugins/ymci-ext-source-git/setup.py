from setuptools import setup, find_packages

setup(
    name='ymci-ext-source-git',
    version='1.0',
    description='Git source plugin for ymci',
    author="Florian Mounier, Kozea",
    author_email="florian.mounier@kozea.fr",

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_source_git'],
    packages=find_packages(),

    entry_points={
        'ymci.ext': [
            'ymci-ext-source-git = ymci_ext_source_git'
        ],
        'ymci.ext.hooks.BuildHook': [
            'git = ymci_ext_source_git.git:GitHook'
        ],
    }
)
