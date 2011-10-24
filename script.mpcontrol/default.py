
import sys
import xbmcaddon
import os

# Addon class
#__language__ = __settings__.getLocalizedString
#_ = sys.modules[ "__main__" ].__language__
#LANGUAGE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'language' ) )
#MEDIA_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'skins' ) )
#sys.path.append (LANGUAGE_RESOURCE_PATH)

if ( __name__ == "__main__" ):

	Addon = xbmcaddon.Addon( id="script.mpcontrol" )
	__cwd__ = Addon.getAddonInfo('path')
	BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
	sys.path.append (BASE_RESOURCE_PATH)

	import mpplayer
	mpplayer.MPCPlayer( xbmc.PLAYER_CORE_PAPLAYER, Addon=Addon, gui=sys.argv )

