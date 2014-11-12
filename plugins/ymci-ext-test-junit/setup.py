from setuptools import setup, find_packages

setup(
    name='ymci-ext-test-junit',
    version='1.1',
    description='Junit test result plugin for ymci',
    author="Florian Mounier, Kozea",
    author_email="florian.mounier@kozea.fr",

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_test_junit'],
    packages=find_packages(),

    entry_points={
        'ymci.ext': [
            'ymci-ext-test-junit = ymci_ext_test_junit'
        ],
        'ymci.ext.hooks.BuildHook': [
            'junit = ymci_ext_test_junit.hooks:JunitHook'
        ],
        'ymci.ext.db.Table': [
            'result = ymci_ext_test_junit.db:Result',
            'config = ymci_ext_test_junit.db:JUnitConfig'
        ],
        'ymci.ext.routes.Route': [
            'result_chart = ymci_ext_test_junit.routes:ResultChart'
        ],
        'ymci.ext.form.Form': [
            'form = ymci_ext_test_junit.form:JUnitForm'
        ]
    }
)
