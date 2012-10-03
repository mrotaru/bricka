from waflib.ConfigSet import ConfigSet
from waflib.Node import Node

def configure( ctx ):

    # load default settings
    ctx.env = ConfigSet('config/default.txt')

    # load tools
    ctx.load( 'htmlcompressor' )
    ctx.load( 'minifier' )

def build( bld ):

    # which files to process ? By default, all html and js
    sources = bld.path.ant_glob( ['**/*.html', '**/*.js'] )

    for s in sources:
        bld( source=s )
