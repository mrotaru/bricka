#!/usr/bin/env python
# encoding: utf-8

"""
A waf tool for minifying javascript.
(http://code.google.com/p/htmlcompressor)
"""

import os
from waflib import Task
from waflib.TaskGen import extension

class minify_js( Task.Task ):
    color = 'BLUE'
    run_str = 'java -jar ${closure_compiler} ${jsminifier_options} --js ${SRC} --js_output_file ${TGT}'

@extension( '.js' )
def html_hook( self, node ):
    """
    Bind the 'js' extension to the `minify_js` task

    :param node: input file
    :type node: :py:class:`waflib.Node.Node`
    """
    self.create_task( 'minify_js', node, node.get_bld() )

def configure( conf ):
    conf.env['closure_compiler'] = os.path.abspath( conf.find_file( 'closure-compiler-v1346.jar', ['.','./tools' ] ) )
