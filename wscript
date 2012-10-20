# vim: filetype=python:
from waflib.ConfigSet import ConfigSet
from waflib.Node import Node
from waflib import Build

def configure( ctx ):

    # load default settings
    ctx.env = ConfigSet('config/default.txt')

    # load tools
#    ctx.load( 'minifier', tooldir='.' )
#    ctx.load( 'compressor', tooldir='.' )
    ctx.load( 'concat', tooldir='.' )

def build( bld ):
    bld.post_mode = Build.POST_LAZY

    # look for html files, which will be compressed.
    sources = bld.path.ant_glob( ['*.html'], exc='build' )
    bld( features='html', source_list = sources )
