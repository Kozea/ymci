from ymci.ext.hooks import BuildHook
from logging import getLogger
from xml.etree import ElementTree
from .db import Coverage
import os

log = getLogger('ymci')


class CoverageHook(BuildHook):

    @property
    def active(self):
        return self.build.project.coverage and self.build.project.coverage.coverage_path is not None

    def post_build(self):
        results = os.path.join(self.build.dir,
                               self.build.project.coverage.coverage_path)
        if os.path.exists(results):
            tree = ElementTree.parse(results)
            root = tree.getroot()
            coverage = Coverage()
            packages = root.find('packages')
            for attr in (
                    'cls', 'missed_cls', 'branches', 'missed_branches',
                    'files', 'missed_files', 'lines', 'missed_lines'):
                setattr(coverage, attr, 0)

            for package in packages:
                coverage.files += 1
                if package.get('line-rate', '0') == '0':
                    coverage.missed_files += 1
                for classes in package:
                    for cls in classes:
                        coverage.cls += 1
                        if cls.get('line-rate', '0') == '0':
                            coverage.missed_cls += 1
                        for lines in cls:
                            for line in lines:
                                coverage.lines += 1
                                if line.get('hits', '0') == '0':
                                    coverage.missed_lines += 1
                                if line.get('branch', 'false') == 'true':
                                    coverage.branches += 1
                                    if line.get('hits', '0') == '0':
                                        coverage.missed_branches += 1

            self.build.coverage = coverage

            self.out(
                'Test coverage: %.2f%% files, %.2f%% classes,'
                ' %.2f%% branches, %.2f%% lines' % (
                    coverage.file_rate,
                    coverage.cls_rate,
                    coverage.branch_rate,
                    coverage.line_rate
                ))
