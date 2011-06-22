#
# Copyright 2011 by Neubloc, LLC. All rights reserved.
# Author: Szymon Rajchman
#

import sys

from django.db import connections, reset_queries

class _TestRunContext(object):
    def __init__(self, name):
        self.udc_values = {}
        self.starting_queries = 0
        self.count = 0
        self.name = name

    def __enter__(self):
        reset_queries()
        for db in connections:
            connection = connections[db]
            self.udc_values[db] = connection.use_debug_cursor
            connection.use_debug_cursor = True
            self.starting_queries += len(connection.queries)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        queries = 0
        for db in connections:
            connection = connections[db]
            connection.use_debug_cursor = self.udc_values[db]
            queries += len(connection.queries)
        self.count = queries - self.starting_queries
        reset_queries()


class QueryStats(object):
    _contextes = {}
    stats = []

    def __getitem__(self, test_name):
        if test_name in self._contextes:
            return self._contextes[test_name].count
        else:
            None

    def context(self, test_name):
        if test_name in self._contextes:
            return self._contextes[test_name]

        context = _TestRunContext(test_name)
        self._contextes[test_name] = context
        self.stats.append((test_name, context))
        return context

    def name(self):
        return "queries"


    def __iter__(self):
        self.stats.sort(lambda x, y: y[1].count - x[1].count)
        return iter(self.stats)

    def print_stats(self, stream=sys.stdout):
        for test_name, context in self:
            stream.write("[%s] %s\n" % (str(context.count).rjust(4), test_name))
