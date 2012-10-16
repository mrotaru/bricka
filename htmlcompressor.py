#!/usr/bin/env python
# encoding: utf-8

"""
A waf tool for **htmlcompressor**
(http://code.google.com/p/htmlcompressor)
"""

import os
from waflib.Configure import conf
from waflib.Task import Task
from waflib.Node import split_path
from waflib.TaskGen import extension, feature, after, after_method
from waflib import Utils, Errors

import utils

class compress_html_base( Task ):
    color = 'PINK'
    run_str = 'java -jar ${htmlcompressor_abspath} ${htmlcompressor_options} ${SRC} -o ${TGT}'

class compress_html( compress_html_base ):
    after = [ 'update_html' ]
    def run( self ):
        compress_html_base.run( self )
        if( self.env[ 'closure_compiler' ] ):
            os.remove( self.inputs[0].abspath() )

@feature( 'html' )
@after_method( 'generate_minification_tasks' )
def generate_html_compression_tasks( self ):
    src = None
    out = None
    for node in self.source_list:
        tools = self.bld.tools
        if 'minifier' in tools:

            # find the 'update_html' task for this node, and get it's output node
            tsk = utils.find_task( self, 'update_html', node.abspath() )
            if tsk:
                src = tsk.outputs[0]
                abspath_out = os.path.join( self.bld.get_variant_dir(), split_path(tsk.inputs[0].abspath())[-1] )
                out = self.bld.root.make_node( abspath_out )
        else: # minifier not loaded
            src = node
            out = node.get_bld()

        self.create_task( 'compress_html', src, out )

def configure( conf ):
    conf.find_program( 'java' )
    conf.env['htmlcompressor_abspath'] = os.path.abspath( conf.find_file( 'htmlcompressor-1.5.3.jar', ['.','./tools' ] ) )
