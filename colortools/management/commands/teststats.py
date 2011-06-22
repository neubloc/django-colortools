#
# Copyright 2011 by Neubloc, LLC. All rights reserved.
# Author: Szymon Rajchman
#

from optparse import make_option

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Print profiler stats for given test."
    args = "teststats [test_name ...]"

    option_list = BaseCommand.option_list + (
        make_option('--file', action='store', dest='file',
            default='.profiler', help='Defines which profiler stats file to use.'),
    )

    def handle(self, *test_names, **options):
        file = options.get('file', '.profiler')

        try:
            import pstats #@UnusedImport
        except:
            self.stderr.write("Couldn't import pstats module")
            return

        from colortools.stats import ColorStats

        stats = ColorStats(file, stream=self.stdout)

        if len(test_names) == 0:
            stats.print_tests_report()
        else:
            stats.print_callees(*test_names)
