from ymci.ext.hooks import BuildHook

import os
from collections import defaultdict
from glob import glob
from .db import Sloccount


class SloccountHook(BuildHook):

    @property
    def active(self):
        return (self.build.project.sloccount and
                self.build.project.sloccount.sloccount_path)

    def validate_build(self):
        scs = glob(
            os.path.join(self.build.dir,
                         self.build.project.sloccount.sloccount_path))
        for sc in scs:
            values = defaultdict(int)
            with open(sc, 'r') as sloc:
                lines = sloc.read()
            _, sloc = lines.split('\n\n\n')

            for line in sloc.splitlines():
                count, language = line.split('\t')[0:2]
                values[language] += int(count)

            for language, value in values.items():
                sloccount = Sloccount()
                sloccount.filename = sc
                sloccount.language = language
                sloccount.count = value
                self.build.sloccounts.append(sloccount)

            self.out('Source Lines of Code: %s' % ', '.join(
                ['%s %s lines' % (value, language) for language, value in
                 values.items()]))
