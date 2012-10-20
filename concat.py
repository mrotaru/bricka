#!/usr/bin/env python
# encoding: utf-8

"""
A waf tool for concatenating JavaScript and CSS files.

It looks for blocks like:
<!-- wbs: concat > jquery.js -->
<script src="js/libs/jquery-1.8.0.js"></script>
<script src="js/libs/jquery-ui-1.8.20.custom.min.js"></script>
<!-- end-wbs -->
And:
<!-- wbs: concat > main.css -->
<link rel="stylesheet" href="css/normalize.css">
<link rel="stylesheet" href="css/main.css">
<!-- end-wbs -->
"""

import re
import os
from HTMLParser import HTMLParser

from waflib.TaskGen import extension, feature, after_method, taskgen_method
from waflib.Task import Task
from waflib import Build, Logs

import utils

#-------------------------------------------------------------------------------
def concatenate_files_fun( task ):
    files = []
    for file in task.inputs:
        files.append( file.abspath() )
    result = ''.join( read_entirely( file ) for file in files )
    with open( task.outputs[0].abspath(), 'w') as handle:
        handle.write( result )

# {{{ extracts blocks which contain stuff to be concatenated Using the example at
# the top, after parsing is complete, `blocks` would contain two items, each
# with two strings pointing to the respective files. 
#-------------------------------------------------------------------------------
class GetConcatBlocks( HTMLParser ):
    
    wbs_concat_regex    = re.compile( '\s*wbs:\s*concat\s*>\s*([A-Za-z.\-]+)\s*' )
    wbs_end_regex       = re.compile( '\s*wbs:\s*end\s*' )

    # regexes for CDNs
    google_cdn_regex        = re.compile( r'//ajax.googleapis.com/ajax/libs/(.*?)/(.*?)/(.*)\.js' )
    microsoft_cdn_regex     = re.compile( r'//ajax.aspnetcdn.com/ajax/(.*?)/(.*)\.js' )
    cdnjs_cdn_regex         = re.compile( r'//cdnjs.cloudflare.com/ajax/libs/(.*?)/(.*?)/(.*)\.js' )

    def __init__( self ):
        HTMLParser.__init__( self )
        self.inside = False
        self.blocks = {}
        self.current_block = None

    def handle_comment( self, data ):

        # start of concat block ?
        match_start = self.wbs_concat_regex.search( data )
        if match_start:
            out_file = match_start.group(1)
            self.blocks[ out_file ] = {}
            self.current_block = self.blocks[ out_file ]
            self.current_block['start'] = self.getpos()[0]
            self.current_block['files'] = []
            self.inside = True
        else:
            # end of concat block ?
            match_end = self.wbs_end_regex.search( data )
            if match_end:
                self.current_block[ 'end'] = self.getpos()[0]
                self.inside = False
    
    def handle_starttag( self, tag, attrs ):
        if tag == 'script':
            if self.inside:
                for name,value in attrs:
                    if name == 'src':
                        if(     self.google_cdn_regex.search( value ) or
                                self.microsoft_cdn_regex.search( value ) or
                                self.cdnjs_cdn_regex.search( value ) ):
                            Logs.warn( 'concat: ignoring CDN script: %s' % value )
                        else:
                            self.current_block['files'].append( value )
        elif tag == 'link':
            if self.inside:
                is_css = False
                css_href = ''
                for name,value in attrs:
                    if( name == 'rel' and value == 'stylesheet' ):
                        is_css = True
                    elif( name == 'href' ):
                        css_href = value
                if( is_css ):
                    if( css_href ):
                        self.current_block['files'].append( css_href ) # }}}

# from: http://stackoverflow.com/a/11659969/447661
#-------------------------------------------------------------------------------
def read_entirely( file ):
    with open( file, 'r' ) as handle:
        return handle.read()

# update the HTML file to reference the concatenated files
#-------------------------------------------------------------------------------
def update_concat_fun( task ):
    pass

#-------------------------------------------------------------------------------
def get_bocks( abspath ):
    p = GetConcatBlocks()
    p.feed( read_entirely( abspath ) )
    return p.blocks

#-------------------------------------------------------------------------------
class generate_concatenation_tasks( Task ):
    after = [ 'minifier_update' ]

    def run( self ):
        blocks = get_bocks( self.inputs[0].abspath() )
        gb = self.generator.bld
        for block in blocks:
            Logs.debug( 'concatenating %r' % blocks[block] )
            inputs = [] # files to be concatenated
            for css in blocks[ block ]['files']:
                css_node = self.generator.bld.bldnode.find_resource( css )
                if css_node:
                    inputs.append( css_node )
                else:
                    Logs.warn( 'file %s not found' % css_node.abspath() )
            gb.add_group()
            gb( name='concatenate', color='CYAN', rule=concatenate_files_fun, source=inputs, target=block ) 
        gb( name='concat_update', color='PINK', rule=update_concat_fun, source=self.inputs[0], after='concatenate_files_fun', blocks = blocks )

#-------------------------------------------------------------------------------
@feature( 'html' )
@after_method( 'generate_minification_tasks' )
def concatenation_tasks( self ):
    for node in self.source_list:
        src = self.bld.path.find_resource( node.nice_path() ) or node
        out = node.get_bld()
        self.create_task( 'generate_concatenation_tasks', src, None )

#-------------------------------------------------------------------------------
def configure( conf ):
    pass
