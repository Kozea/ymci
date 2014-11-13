from ymci.ext.hooks import BuildHook, FormHook
from ymci import server
from logging import getLogger
from xml.etree import ElementTree
from glob import glob
from .db import Coverage
import os

log = getLogger('ymci')


class CoverageHook(BuildHook):

    @property
    def active(self):
        return (self.build.project.coverage and
                self.build.project.coverage.coverage_path)

    def validate_build(self):
        projects_path = server.conf['projects_realpath']
        try:
            with open(os.path.join(
                    self.build.dir,
                    'ymci_ext_coverage_config.yaml'), 'w') as fd:
                fd.write('coverage_path:\n')
                fd.write(
                    '%s%s' % (' '*4, os.path.join(
                        projects_path, self.build.project.dir_name,
                        'build_%d' % self.build.build_id,
                        self.build.project.coverage.coverage_path)))
        except Exception:
            log.warning('Error with coverage.ymal', exc_info=True)

        results = glob(
            os.path.join(self.build.dir,
                         self.build.project.coverage.coverage_path))
        for result_file in results:
            tree = ElementTree.parse(result_file)
            root = tree.getroot()
            coverage = Coverage()
            coverage.filename = result_file
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

            self.build.coverages.append(coverage)

            self.out(
                'Test coverage: %.2f%% files, %.2f%% classes,'
                ' %.2f%% branches, %.2f%% lines' % (
                    coverage.file_rate,
                    coverage.cls_rate,
                    coverage.branch_rate,
                    coverage.line_rate
                ))


class CoverageFormHook(FormHook):
    def pre_populate(self, form):
        form.coverage.coverage_path.data = (
            form.coverage.coverage_path.data.lstrip('./'))
        return True
