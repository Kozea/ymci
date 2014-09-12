from ymci.ext.hooks import BuildHook

import os
from collections import defaultdict

from .db import Sloccount


class SloccountHook(BuildHook):

    @property
    def active(self):
        return True

    def validate_build(self):
        sloccount_file = os.path.join(self.build.dir, 'sloccount.sc')
        if os.path.exists(sloccount_file):
            values = defaultdict(int)
            with open(sloccount_file, 'r') as sloc:
                for line in sloc.readlines():
                    count, language = line.split('\t')[0:2]
                    values[language] += int(count)
            for language in values.keys():
                self.build.sloccounts.append(Sloccount(
                    language=language, count=values[language]))
            self.out('Source Lines of Code: %s' % ', '.join(
                ['%s %s lines' % (count, language) for language, count in
                 values.items()]))
