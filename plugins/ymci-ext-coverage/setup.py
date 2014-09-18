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
    package_data={'ymci_ext_coverage': ['templates/*', 'static/*']},
    entry_points={
        'ymci.ext': [
            'ymci-ext-coverage = ymci_ext_coverage'
        ],
        'ymci.ext.hooks.BuildHook': [
            'coverage = ymci_ext_coverage.hooks:CoverageHook'
        ],
        'ymci.ext.hooks.FormHook': [
            'coverage = ymci_ext_coverage.hooks:CoverageFormHook'
        ],
        'ymci.ext.db.Table': [
            'result = ymci_ext_coverage.db:Coverage',
            'config = ymci_ext_coverage.db:CoverageConfig'
        ],
        'ymci.ext.routes.Route': [
            'result_chart = ymci_ext_coverage.routes:CoverageChart',
            'browse_coverage = ymci_ext_coverage.routes:BrowseCoverage'
        ],
        'ymci.ext.form.Form': [
            'form = ymci_ext_coverage.form:CoverageForm'
        ]
    }
)
