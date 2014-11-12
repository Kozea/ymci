from ymci.ext.hooks import BuildHook
from logging import getLogger
from xml.etree import ElementTree
from .db import Result
from glob import glob
import os

log = getLogger('ymci')


class JunitHook(BuildHook):

    @property
    def active(self):
        return (self.build.project.junit and
                self.build.project.junit.junit_path)

    def validate_build(self):
        results = glob(os.path.join(
            self.build.dir, self.build.project.junit.junit_path))
        for result_file in results:
            result = Result()
            result.filename = result_file
            result.error = 0
            result.fail = 0
            result.skip = 0
            result.total = 0

            tree = ElementTree.parse(result_file)
            testsuite = tree.getroot()
            for testcase in testsuite:
                if len(testcase):
                    failtype = testcase[0].tag
                    if failtype == 'failure':
                        result.fail += 1
                    elif failtype == 'error':
                        result.error += 1
                    elif failtype == 'skipped':
                        result.skip += 1

                result.total += 1

            if result.fail + result.error != 0:
                self.build.status = 'FAILED'
            self.build.results.append(result)
            self.out(
                'Build (%s) is %s: %d tests run, '
                '%d errors %d fails %d skips %d success' % (
                    result.filename,
                    self.build.status,
                    result.total,
                    result.error,
                    result.fail,
                    result.skip,
                    result.success))
