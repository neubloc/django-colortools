#
# Copyright 2011 by Neubloc, LLC. All rights reserved.
# Author: Szymon Rajchman
#

import re
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
import unipath


ORDER = [
    'calls', # call count
    'cumulative', # cumulative time
    'file', # file name
    'module', # file name
    'pcalls', # primitive call count
    'line', # line number
    'name', # function name
    'nfl', # name/file/line
    'stdname', # standard name
    'time', # internal time
]
DEFAULT_ORDER = 1

REPORT = [
    'stats',
    'callees',
    'callers',
]
DEFAULT_REPORT = 0

class Command(BaseCommand):
    help = "Print profiler stats for given test."
    args = "test_name [test_name ...]"

    option_list = BaseCommand.option_list + (
        make_option('--file', action='store', dest='file',
            default='.profiler', help='Defines which profiler stats file to use.'),
        make_option('--order', action='store', dest='order',
            default=ORDER[DEFAULT_ORDER], help='Defines sorting order.',
            choices=ORDER),
        make_option('--report', action='store', dest='report',
            default=REPORT[DEFAULT_REPORT], help='Defines report type.',
            choices=REPORT)
    )

    def handle(self, *args, **options):
        file = options.get('file', '.profiler')
        path = unipath.Path(file)
        if not path.exists() or not path.isfile():
            raise CommandError("Provided statistics file does not exist (%s)" %
                                   path)

        order = options.get('order', ORDER[DEFAULT_ORDER])

        report = options.get('report', REPORT[DEFAULT_REPORT])

        try:
            import pstats #@UnusedImport
        except:
            raise CommandError("Couldn't import pstats module")

        from colortools.stats import ColorStats

        stats = ColorStats(file, stream=self.stdout)

        stats.sort_stats(order)

        # process args
        params = []
        restriction = '\(test\_*'
        for arg in args:
            if re.match('^\d+$', arg):
                params.append(int(arg))
            elif re.match('^\d*\.\d+$', arg):
                params.append(float(arg))
            else:
                restriction = arg

        params.insert(0, restriction)
        print params

        if report == 'callers':
            stats.print_callers(*params)
        elif report == 'callees':
            stats.print_callees(*params)
        else:
            stats.print_stats(*params)

