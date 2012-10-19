#!/usr/bin/env python
# encoding: utf-8

from waflib.Task import Task

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
