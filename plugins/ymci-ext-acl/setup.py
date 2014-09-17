from setuptools import setup, find_packages

setup(
    name='ymci-ext-acl',
    version='1.0',
    description='ACL rights plugin for ymci',
    author='Jean-Marc Martins, Kozea',
    author_email='jmartins@kozea.fr',

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_acl'],
    packages=find_packages(),

    entry_points={
        'ymci.ext.db.Table': [
            'acl_table = ymci_ext_acl.db:Acl'
        ],
        'ymci.ext.hooks.PrepareHook': [
            'acl_hook = ymci_ext_acl.hooks:AclHook'
        ]
    }
)
