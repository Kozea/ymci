from setuptools import setup, find_packages

setup(
    name='ymci-ext-mail-alerts',
    version='1.1.0',
    description='Mail alert plugin for ymci',
    author='Jean-Marc Martins, Kozea',
    author_email='jmartins@kozea.fr',

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_mail_alerts'],
    packages=find_packages(),

    entry_points={
        'ymci.ext': [
            'ymci-ext-mail-alerts = ymci_ext_mail_alerts'
        ],
        'ymci.ext.hooks.BuildHook': [
            'mail_alerts = ymci_ext_mail_alerts.mail:MailHook'
        ],
    }
)
