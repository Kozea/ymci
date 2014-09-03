from setuptools import setup, find_packages

setup(
    name='ymci-ext-coverage',
    version='1.0',
    description='Coverage (cobertura) plugin for ymci',
    author="Florian Mounier, Kozea",
    author_email="florian.mounier@kozea.fr",

    platforms=['Any'],

    scripts=[],

    provides=['ymci_ext_coverage'],
    packages=find_packages(),

    entry_points={
        'ymci.ext.hooks.BuildHook': [
            'coverage = ymci_ext_coverage.coverage:CoverageHook'
        ],
        'ymci.ext.db.Table': [
            'result = ymci_ext_coverage.db:Coverage'
        ],
        'ymci.ext.routes.Route': [
            'result_chart = ymci_ext_coverage.routes:CoverageChart'
        ],
    }
)
