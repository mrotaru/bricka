#!/usr/bin/env python
# encoding: utf-8

from waflib.Task import Task
import string

def find_task( tgen, tname, abspath ):
    """{{{
    Go through `tgen`'s `tname` tasks, and return the first one that
    has an input node with an absolute path equal to `abspath`.
    }}}"""
    for tsk in tgen.tasks:
        if( tsk.__class__.__name__ == tname ):
            for node in tsk.inputs:
                if( node.abspath() == abspath ):
                    return tsk
    return None

def first_non_blank( mstring, tabsize=4 ): 
    """{{{;
    Returns the zero-based index of the first non-blank character of a string.
    If tabsize argument is provided, tabs are expanded. Otherwise, a tab counts
    as 1 non-blank character.
    }}}"""
    mstring.expandtabs( tabsize )
    i=0
    for char in mstring:
        if char in string.whitespace:
            i = i + 1
        else:
            return i
    return -1

def print_tasks( tgen ):
    """
    Pretty-print a task generator's tasks, for debugging purposes.
    """
    if len( tgen.tasks ):
        for t in tgen.tasks:
            print t
    else:
        print 'no tasks for ' + str( tgen )
