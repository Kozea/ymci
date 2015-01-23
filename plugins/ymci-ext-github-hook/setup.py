from setuptools import setup, find_packages

setup(
    name='ymci-ext-github-hook',
    version='1.0.0',
    description='Github hook plugin',
    author="Florian Mounier, Kozea",
    author_email="florian.mounier@kozea.fr",

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_github_hook'],
    packages=find_packages(),
    entry_points={
        'ymci.ext': [
            'ymci-ext-github-hook = ymci_ext_github_hook'
        ],
        'ymci.ext.routes.Route': [
            'hook = ymci_ext_github_hook.routes:GithubHook'
        ]
    }
)
