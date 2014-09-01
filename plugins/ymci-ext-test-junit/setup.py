from setuptools import setup, find_packages

setup(
    name='ymci-ext-test-junit',
    version='1.0',
    description='Junit test result plugin for ymci',
    author="Florian Mounier, Kozea",
    author_email="florian.mounier@kozea.fr",

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_test_junit.junit'],
    packages=find_packages(),

    entry_points={
        'ymci.ext.hooks.BuildHook': [
            'junit = ymci_ext_test_junit.junit:JunitHook'
        ],
        'ymci.ext.db.Table': [
            'result = ymci_ext_test_junit.db:Result'
        ],
        'ymci.ext.routes.Route': [
            'result_chart = ymci_ext_test_junit.routes:ResultChart'
        ],
    }
)
