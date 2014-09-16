from ymci.ext.hooks import BuildHook
from logging import getLogger
from xml.etree import ElementTree
from .db import Result
import os

log = getLogger('ymci')


class JunitHook(BuildHook):

    @property
    def active(self):
        return (self.build.project.junit and
                self.build.project.junit.junit_path)

    def validate_build(self):
        results = os.path.join(self.build.dir, 'results.xml')
        if os.path.exists(results):
            tree = ElementTree.parse(results)
            node = tree.getroot()
            result = Result()
            result.error = int(node.get('errors', 0))
            result.fail = int(node.get('failures', 0))
            result.skip = int(node.get('skips', node.get('skip', 0)))
            result.total = int(node.get('tests', 0))

            if result.fail + result.error == 0:
                self.build.status = 'SUCCESS'
            else:
                self.build.status = 'FAILED'
            self.build.result = result
            self.out(
                'Build is %s: %d tests run, '
                '%d errors %d fails %d skips %d success' % (
                    self.build.status,
                    result.total,
                    result.error,
                    result.fail,
                    result.skip,
                    result.success))
