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
from HTMLParser import HTMLParser

from waflib.TaskGen import extension, feature

# extracts blocks which contain stuff to be concatenated Using the example at
# the top, after parsing is complete, `blocks` would contain two items, each
# with two strings pointing to the respective files.
#-------------------------------------------------------------------------------
class GetConcatBlocks( HTMLParser ):
    
    wbs_concat_regex    = re.compile( '\s*wbs:\s*concat\s*>\s*([A-Za-z.\-]+)\s*' )
    wbs_end_regex       = re.compile( '\s*wbs:\s*end\s*' )
    inside = False
    blocks = []

    def handle_comment( self, data ):

        # start of concat block ?
        match_start = self.wbs_concat_regex.search( data )
        if match_start:
            print "start %s" % match_start.group(1)

            inside = True
        else:
            # end of concat block ?
            match_end = self.wbs_end_regex.search( data )
            if match_end:
                print "<end>"
                inside = False
    
    def handle_starttag( self, tag, attrs ):
        if tag == 'link':
            print "encountered a link: " + str(attrs)

    def handle_endtag( self, tag ):
        pass

# from: http://stackoverflow.com/a/11659969/447661
#-------------------------------------------------------------------------------
def read_entirely( file ):
    with open( file, 'r' ) as handle:
        return handle.read()

# generate a file which will consist of all files in `files` concatenated
#-------------------------------------------------------------------------------
def concatenate_files( dest, *files ):
    result = '\n'.join( read_entirely( file ) for file in files )
    with open(file, 'w') as handle:
        handle.write( result )

# will scan the file, concatenate detected scripts and update `file`
#-------------------------------------------------------------------------------
@extension( '.html' )
def scan_for_concatenations( self, node ):
    p = GetConcatBlocks()
    p.feed( read_entirely( node.abspath() ) )
