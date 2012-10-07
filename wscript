from waflib.ConfigSet import ConfigSet
from waflib.Node import Node

def configure( ctx ):

    # load default settings
    ctx.env = ConfigSet('config/default.txt')

    # load tools
#    ctx.load( 'htmlcompressor' )
    ctx.load( 'minifier' )

def build( bld ):

    # look for html files, which will be compressed.
    sources = bld.path.ant_glob( ['**/*.html'] )

    for s in sources:
        bld( source=s )
