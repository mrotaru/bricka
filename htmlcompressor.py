#!/usr/bin/env python
# encoding: utf-8

"""
A waf tool for **htmlcompressor**
(http://code.google.com/p/htmlcompressor)
"""

import os
from waflib.Configure import conf
from waflib.Task import Task
from waflib import Utils
from waflib.TaskGen import extension, feature, after

class compress_html( Task ):
    after = [ 'minify_js', 'minify_css', 'update_html' ]
    color = 'PINK'
    run_str = 'java -jar ${htmlcompressor_abspath} ${htmlcompressor_options} ${SRC} -o ${TGT}'

@feature( 'html' )
@after( 'generate_minification_tasks' )
def generate_html_compression_tasks( self ):

    for node in self.source_list:
        if( self.env[ 'closure_compiler' ] ):

            # find the 'update_html' task for this node, and get it's output node
            for tsk in self.tasks:
                if( tsk.__class__.__name__ == 'update_html' ):
                    if( tsk.inputs[0].abspath() == node.abspath() ):
                        src = tsk.outputs[0]
                        out = self.path.make_node( str(node) )
        else: # minifier not loaded
            src = node
            out = node.get_bld()

        self.create_task( 'compress_html', src, out )

def configure( conf ):
    conf.find_program( 'java' )
    conf.env['htmlcompressor_abspath'] = os.path.abspath( conf.find_file( 'htmlcompressor-1.5.3.jar', ['.','./tools' ] ) )
