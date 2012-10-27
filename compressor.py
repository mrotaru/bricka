#!/usr/bin/env python
# encoding: utf-8

"""
A waf tool for **htmlcompressor**
(http://code.google.com/p/htmlcompressor)
"""

import os
from waflib.Configure import conf
from waflib.Task import Task, compile_fun, ASK_LATER, RUN_ME
from waflib.Node import split_path
from waflib.TaskGen import extension, feature, after, after_method
from waflib import Utils, Errors

import utils

class compress_html_base( Task ):
    color = 'PINK'
    no_output_fun = compile_fun( 'java -jar ${htmlcompressor_abspath} ${htmlcompressor_options} ${SRC} -o ${SRC[0].get_bld().abspath()}' )[0]
    w_output_fun  = compile_fun( 'java -jar ${htmlcompressor_abspath} ${htmlcompressor_options} ${SRC} -o ${TGT}' )[0]

    def run( self ):
        if not self.outputs:
            return compress_html_base.no_output_fun( self )
        else:        
            return compress_html_base.w_output_fun( self )

class compress_html( compress_html_base ):
    after = [ 'update_minifier', 'generate_concatenation_tasks', 'concat_update' ]

#    def runnable_status( self ):
#        b = self.generator.bld
#        g = self.generator
#        tgg = None # task generator group
#        if b.tools['minifier']:
#            try:
#                tgg = b.group_names['concatenations']
#            except:
#                pass

#            # return 'ASK_LATER' if 'concat_update' task hasn't been completed
#            if tgg:
#                for tg in tgg:
#                    print tg.name
#                    if tg.name == 'concat_update':
#                        if len(tg.tasks):
#                            print 'have tasks:'
#                            for tsk in tg.tasks:
#                                print tsk
#                                print 'RUNNING!'
#                                return RUN_ME
#                        else:
#                            print 'LATER!'
#                            return ASK_LATER
#        return ASK_LATER
    def run( self ):
        print self.inputs[0].abspath()
        print self.outputs[0].abspath()
        compress_html_base.run( self )

@feature( 'html' )
@after_method( 'generate_minification_tasks' )
@after_method( 'generate_concatenation_tasks' )
def generate_html_compression_tasks( self ):
    for node in self.source_list:
        src = self.bld.bldnode.find_node( node.nice_path() ) or node
        print 'compress src: %s' % src.abspath()
        out = src.get_bld()
        print 'compress out: %s' % out.abspath()
        if src.abspath() == src.get_bld().abspath():
            out.sig = None
            out.parent.mkdir()
        inp = [node]
        self.create_task( 'compress_html', src, out )

def configure( conf ):
    conf.find_program( 'java' )
    conf.env['htmlcompressor_abspath'] = os.path.abspath( conf.find_file( 'htmlcompressor-1.5.3.jar', ['.','./tools' ] ) )
