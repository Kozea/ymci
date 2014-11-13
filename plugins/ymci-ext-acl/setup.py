from setuptools import setup, find_packages

setup(
    name='ymci-ext-acl',
    version='1.1',
    description='ACL rights plugin for ymci',
    author='Jean-Marc Martins, Kozea',
    author_email='jmartins@kozea.fr',

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_acl'],
    packages=find_packages(),
    package_data={'ymci_ext_acl': ['templates/*', 'static/*']},

    entry_points={
        'ymci.ext.routes.Route': [
            'acl_route = ymci_ext_acl.routes:RightsList'
        ],
        'ymci.ext': [
            'ymci-ext-acl = ymci_ext_acl'
        ],
        'ymci.ext.db.Table': [
            'acl_table = ymci_ext_acl.db:Acl'
        ],
        'ymci.ext.hooks.PrepareHook': [
            'acl_hook = ymci_ext_acl.hooks:AclHook'
        ]
    }
)
