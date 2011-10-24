import xbmc
import xbmcgui
import mpcinterface
from threading import Timer

class MPCPlayer( xbmc.Player ):

	PAUSE = 10001
	RESUME = 10002
	START = 10003
	SWAP = 10004

	AUTO = 100
	MANUAL = 101
	MPC = 102
	XBMC = 103

	currentMode = None
	currentAudio = None
	lastXBMCVolume = 0
	ready = False
	failure = False
	client = None

	def __init__( self, *args, **kwargs ):
		xbmc.Player.__init__(self)
		self.ready = False
		self.failure = False
		self.client = None
		self.host = 'cerberus.local'
		self.port = 6600
		self.use_gui = kwargs[ "gui" ]
		self.Addon = kwargs[ "Addon" ]
		self.currentMode = self.AUTO
		self.currentAudio = self.XBMC
		self.lastXBMCVolume = int(xbmc.executehttpapi("GetVolume").strip('<li>'))
		xbmc.log( 'gui is %s' % self.use_gui, xbmc.LOGNOTICE )

		if len(self.use_gui) == 2:
			if self.use_gui[1] == 'swap':
				self._perform_swap()
		else:
			self.action(self.START)
			self._start_background()

	def _perform_swap( self ):
		xbmc.log('mpcControl: doing a mute swap', xbmc.LOGNOTICE)
		self.action( self.SWAP );
		return True
		
	def _start_background( self ):
		self.loop = True
		xbmc.log('mpcControl: time to go loopy... see you on the flip side..', xbmc.LOGNOTICE)
		while (not xbmc.abortRequested):
			xbmc.sleep( 2000 )
		xbmc.log('mpcControl: loopy log exited.. it must be time to say goodbye...', xbmc.LOGNOTICE)

	def onPlayBackStarted(self):
		xbmc.log('mpcControl: playbackstart, asking for pause', xbmc.LOGNOTICE)
		self.action(self.PAUSE)

	def onPlayBackResumed(self):
		xbmc.log('mpcControl: playbackresume, asking for resume', xbmc.LOGNOTICE)
		#self.action(self.PAUSE)

	def onPlayBackPaused(self):
		xbmc.log('mpcControl: playbackpause, asking for resume', xbmc.LOGNOTICE)
		#self.action(self.RESUME)

	def onPlayBackStopped(self):
		xbmc.log('mpcControl: playbackstop, asking for resume', xbmc.LOGNOTICE)
		self.action(self.RESUME)

	def onPlayBackEnded(self):
		xbmc.log('mpcControl: playbackend, asking for resume', xbmc.LOGNOTICE)
		self.action(self.RESUME)



    ######################################################################

	def action(self, action):

		self.status = None

		if self.client == None or self.ready == False:
			self.client = mpcinterface.MPDClient()
			self.client.connect(self.host,int(self.port))
			self.ready = True
			xbmc.log("mpcControl: connected", xbmc.LOGNOTICE)
		
		try:
			xbmc.sleep(200)
			self.status = self.client.status()
			xbmc.log("mpcControl: current state (pre event) is %s" % self.status['state'],  xbmc.LOGNOTICE)
		except:
			self.ready = False

		# actions to apply in all modes
		if action == self.SWAP: return self.actionSWAP()
	
		# actions to apply in Auto Mode
		if self.currentMode != self.AUTO: return True
		if action == self.RESUME: return self.actionRESUME()
		if action == self.PAUSE: return self.actionPAUSE() 
		if action == self.START: return self.actionSTART()

		xbmc.log("mpcControl: unknown action %d" % action, xbmc.LOGNOTICE)
		return False

	def actionSWAP(self):
		oldMode = self.currentMode

		if self.currentAudio == self.MPC:
			self.stopLocalMusic()
			xbmc.sleep(500)
			self.currentAudio = self.XBMC
			self.currentMode = self.MANUAL
			self.setXBMCVolume(self.lastXBMCVolume)
		else:
			self.lastXBMCVolume = 90
			xbmc.sleep(500)
			self.currentAudio = self.MPC
			self.currentMode = self.MANUAL
			self.setXBMCVolume(0)
			self.startLocalMusic()

		return self.currentAudio


	def actionRESUME(self):				
		# sleep for a little while before we bring the music back

		xbmc.log("mpcControl: waiting for xbmc to stop playing", xbmc.LOGNOTICE )
		counter = 0
		while ( not xbmc.abortRequested and self.isPlaying() and counter < 5 ):
			xbmc.sleep( 1000 )
		if self.isPlaying(): return
		self.startLocalMusic()
		return True

	def actionPAUSE(self):
		self.stopLocalMusic()
		return True
	
	def actionSTART(self):	
		if int(self.status['playlistlength']) > 0:
			self.startLocalMusic()
			return True
		else:
			xbmc.executebuiltin("XBMC.Notification(%s,%s,5000)" % ( 'Music Server', 'Playlist is Empty' ))
			return False



	def done(self):
		xbmc.log("done", xbmc.LOGNOTICE)


	def stopLocalMusic(self):
		self.client.pause()
		self.currentMode = self.XBMC
		return True

	def startLocalMusic(self):
		xbmc.executebuiltin("XBMC.Notification(%s,%s,5000)" % ('Music Server', 'Resumiing Playlist'))
		self.currentMode = self.MPC
		self.client.play()
		return True

	def setXBMCVolume(self, newVolume):
		volume = int(xbmc.executehttpapi("GetVolume").strip('<li>'))
		if(volume > 0): self.lastXBMCVolume = volume
		xbmc.executehttpapi("SetVolume(%d)" % newVolume)
		return volume


xbmc.log("mpcControl: running in %s" % __name__, xbmc.LOGNOTICE)
if ( __name__ == "__main__" ):
    MPCPlayer( xbmc.PLAYER_CORE_PAPLAYER )


