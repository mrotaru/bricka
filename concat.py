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

from waflib.TaskGen import extension, feature, after_method
from waflib.Task import Task

import utils

class concatenate( Task ):
    def run( self ):
        print 'files: '
        print self.files

class update_after_concat( Task ):
    pass

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

class scan_for_concatenations( Task ):
    after = [ 'update_html' ]

    def run( self ):
        p = GetConcatBlocks()
        p.feed( read_entirely( self.inputs[0].abspath() ) )
        blocks = p.blocks

        for concat_target in blocks.keys():
            print 'concatenating ' + concat_target
            tgt = self.generator.bld.path.make_node( concat_target )
            tgt.parent.mkdir()
            tsk = self.generator.create_task( 'concatenate', None, tgt, )
            tsk.files = blocks[ concat_target ][ 'files' ]

# generate a file which will consist of all files in `files` concatenated
#-------------------------------------------------------------------------------
def concatenate_files( dest, *files ):
    result = '\n'.join( read_entirely( file ) for file in files )
    with open(file, 'w') as handle:
        handle.write( result )

@feature( 'html' )
@after_method( 'generate_minification_tasks' )
def generate_concatenation_tasks( self ):
    for node in self.source_list:

        tools = self.bld.tools
        if 'minifier' in tools:
            tsk = utils.find_task( self, 'update_html', node.abspath() )
            if tsk:
                node = tsk.outputs[0]
            
        tsk = self.create_task( 'scan_for_concatenations', node, None )

def configure( conf ):
    pass
