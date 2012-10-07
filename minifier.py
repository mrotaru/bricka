#!/usr/bin/env python
# encoding: utf-8

"""
A waf tool for minifying javascript.
(http://code.google.com/p/htmlcompressor)
"""

import os
import re
from HTMLParser import HTMLParser

from waflib import Task
from waflib.TaskGen import extension
from waflib import Logs

# use ClosureCompiler to minify a JavaScript file
#-------------------------------------------------------------------------------
class minify_js( Task.Task ):
    color = 'CYAN'
    run_str = 'java -jar ${closure_compiler} ${jsminifier_options} --js ${SRC} --js_output_file ${TGT}'

# from: http://stackoverflow.com/a/11659969/447661
#-------------------------------------------------------------------------------
def read_entirely( file ):
    with open( file, 'r' ) as handle:
        return handle.read()

# scan an HTML file to detect referenced JavaScript files
#-------------------------------------------------------------------------------
class WBS_HTMLParser( HTMLParser ):

    # regex to detect local fallback for failed CDN requests ( JQuery only )
    inline_js_regex         = re.compile( r'window\.(?i)jquery\s*\|\|\s*document.write\(([\'"])\s*<script\s*src=([\'"])(?P<src>.*?)\2\s*(?:type=\2text/javascript\2\s*)?><\\/script>\1\)' )

    # regexes for CDNs
    google_cdn_regex        = re.compile( r'//ajax.googleapis.com/ajax/libs/(.*?)/(.*?)/(.*)\.js' )
    microsoft_cdn_regex     = re.compile( r'//ajax.aspnetcdn.com/ajax/(.*?)/(.*)\.js' )
    cdnjs_cdn_regex         = re.compile( r'//cdnjs.cloudflare.com/ajax/libs/(.*?)/(.*?)/(.*)\.js' )

    # each detected js file will be added to this list
    local_scripts = []

    # find referenced js files
    def handle_starttag( self, tag, attrs ):
        if( tag == 'script' ):
            for name,value in attrs:
                if( name == 'src' ):
                    if( self.google_cdn_regex.search( value ) or
                            self.microsoft_cdn_regex.search( value ) or
                            self.cdnjs_cdn_regex.search( value ) ):
                        Logs.warn( 'minify: ignoring CDN script: %s' % value )
                    else:
                        self.local_scripts.append( value )

@extension( '.html' )
def html_hook( self, node ):

    # scan the HTML file for script tags
    parser = WBS_HTMLParser()
    parser.feed( read_entirely( node.abspath() ) )
    scripts = parser.local_scripts

    # create a minification task for scripts that are local
    for script in scripts:
        script_node = self.bld.path.find_resource( script )
        if( script_node ):
            dest_script_node = self.bld.path.get_bld().make_node( script )
            print str(dest_script_node)
            self.create_task( 'minify_js', script_node, dest_script_node )
        else:
            Logs.warn( 'minify: script referenced in %s not found: %s' % (node.abspath(), script) )

def configure( conf ):
    conf.env['closure_compiler'] = os.path.abspath( conf.find_file( 'closure-compiler-v1346.jar', ['.','./tools' ] ) )
