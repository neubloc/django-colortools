#
# Copyright 2011 by Neubloc, LLC. All rights reserved.
# Author: Szymon Rajchman
#

import pstats

import unipath
from django.utils import termcolors

class ColorStats(pstats.Stats):
    def __init__(self, *args, **kwargs):
        pstats.Stats.__init__(self, *args, **kwargs)

        class dummy(object): pass
        style = dummy()
        style.LONGRUN = termcolors.make_style(opts=('bold',), fg='red')
        style.NAME = termcolors.make_style(opts=('bold',), fg='cyan')
        style.FILE = termcolors.make_style(opts=('bold',), fg='yellow')
        style.APP = termcolors.make_style(opts=('bold',), fg='white')
        style.HEADER = termcolors.make_style(opts=('bold',), fg='white')
        style.HEADING = termcolors.make_style(opts=('bold',), fg='green')

        self.style = style

    def print_tests_report(self):
        self.sort_stats('cumulative')
        self.print_stats('\(test\_*')

    def print_title(self):
        print >> self.stream, 'calls  cumtime  percall',
        print >> self.stream, 'filename:lineno(function)'

    def print_line(self, func):  # hack : should print percentages
        cc, nc, tt, ct, callers = self.stats[func] #@UnusedVariable
        c = str(nc)
        if nc != cc:
            c = c + '/' + str(cc)
        print >> self.stream, c.rjust(5),
        print >> self.stream, pstats.f8(ct),
        if cc == 0:
            print >> self.stream, ' '*8,
        else:
            percall = float(ct) / cc
            result = pstats.f8(percall)
            if percall > 0.1:
                result = self.style.LONGRUN(result)
            print >> self.stream, result,
        print >> self.stream, self.func_test_string(func)

    def func_test_string(self, func_name): # match what old profile produced
        if func_name[:2] == ('~', 0):
            # special case for built-in functions
            name = func_name[2]
            if name.startswith('<') and name.endswith('>'):
                return '{%s}' % name[1:-1]
            else:
                return name
        else:
            file, line, name = func_name
            file = unipath.Path(file)
            return ("%s (%s:%d [%s])" %
                (self.style.NAME(name),
                 self.style.FILE(file.name), line,
                 self.style.APP(file.parent.parent.name)))

    def print_callees(self, *amount):
        width, list = self.get_print_list(amount)
        width = 2
        if list:
            self.calc_callees()

            self.print_call_heading(width, "called...")
            for func in list:
                if func in self.all_callees:
                    self.print_call_line(width, func, self.all_callees[func])
                else:
                    self.print_call_line(width, func, {})
            print >> self.stream
            print >> self.stream
        return self

    def print_call_heading(self, name_size, column_title):
        print >> self.stream, self.style.HEADING("Function ".ljust(name_size) + column_title)
        # print sub-header only if we have new-style callers
        subheader = False
        for cc, nc, tt, ct, callers in self.stats.itervalues():
            if callers:
                value = callers.itervalues().next()
                subheader = isinstance(value, tuple)
                break
        if subheader:
            print >> self.stream, self.style.HEADER(" "*name_size + "    ncalls  tottime  cumtime")

    def print_call_line(self, name_size, source, call_dict, arrow="->"):
        print >> self.stream, self.func_std_string(source).ljust(name_size) + arrow,
        if not call_dict:
            print >> self.stream
            return
        print >> self.stream
        clist = call_dict.keys()
        clist.sort()
        for func in clist:
            name = self.func_std_string(func)
            value = call_dict[func]
            if isinstance(value, tuple):
                nc, cc, tt, ct = value
                if nc != cc:
                    substats = '%d/%d' % (nc, cc)
                else:
                    substats = '%d' % (nc,)
                substats = '%s %s %s  %s' % (substats.rjust(7 + 2),
                                             pstats.f8(tt), pstats.f8(ct), name)
                left_width = name_size + 1
            else:
                substats = '%s(%r) %s' % (name, value, pstats.f8(self.stats[func][3]))
                left_width = name_size + 3
            print >> self.stream, " " * left_width + substats

    def func_std_string(self, func_name): # match what old profile produced
        if func_name[:2] == ('~', 0):
            # special case for built-in functions
            name = func_name[2]
            if name.startswith('<') and name.endswith('>'):
                return '{%s}' % name[1:-1]
            else:
                return name
        else:
            file, line, name = func_name
            file = unipath.Path(file)
            return ("%s (%s:%d)" %
                (self.style.NAME(name),
                 self.style.FILE(file.relative()), line))
