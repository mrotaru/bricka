#!/usr/bin/env python
# encoding: utf-8

"""
A waf tool for **htmlcompressor**
(http://code.google.com/p/htmlcompressor)
"""

import os
from waflib.Configure import conf
from waflib import Task, Utils
from waflib.TaskGen import extension, feature

class compress_html( Task.Task ):
    color = 'PINK'
    run_str = 'java -jar ${htmlcompressor_abspath} ${htmlcompressor_options} ${SRC} -o ${TGT}'

@extension( '.html', '.php' )
def html_hook( self, node ):
    """
    Bind the html extension to the compress_html task

    :param node: input file
    :type node: :py:class:`waflib.Node.Node`
    """
    self.create_task( 'compress_html', node, node.get_bld() )

def configure( conf ):
    conf.find_program( 'java' )
    conf.env['htmlcompressor_abspath'] = os.path.abspath( conf.find_file( 'htmlcompressor-1.5.3.jar', ['.','./tools' ] ) )
