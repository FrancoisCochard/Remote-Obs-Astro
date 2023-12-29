from transitions import Machine, State
from transitions.extensions import GraphMachine
from Target.Target import Target
from TargetDatabase.TargetBase import TargetBase # Je charge la base de données
from helper.IndiClient import IndiClient
from Mount.Indi10micronMount import Indi10micronMount
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
# Viz stuff
import matplotlib.pyplot as plt
from skimage import img_as_float
from skimage import exposure
# Local stuff : Camera
from Camera.IndiZwoASI120Camera import IndiZwoASI120Camera
from Camera.IndiCamera import IndiCamera
from Camera.IndiZwoASI174MiniCamera import IndiZwoASI174MiniCamera
from Camera.IndiZwoASI183ProCamera import IndiZwoASI183ProCamera
# Others
import time
import os
import sys
# ~ import random
from datetime import date, datetime, timedelta, timezone

class Observations(object):
	
	NextTarget = Target()
	NextTargetCorrected = Target()

	# Define some states. Most of the time, narcoleptic superheroes are just like
	# everyone else. Except for...
	states = ['Standby', 
		State('Opening', on_enter=['start_open']),
		State('Next target', on_enter=['start_next_target']),
		State('Pointing', on_enter=['start_pointing']),
		State('Acquisition', on_enter=['start_acquisition']),
		State('Processing', on_enter=['start_processing']),
		State('Parking', on_enter=['start_parking'])
		]
	
	transitions = [
    { 'trigger': 'Open', 'source': 'Standby', 'dest': 'Opening' },
    { 'trigger': 'DefineTarget', 'source': 'Opening', 'dest': 'Next target' },
    { 'trigger': 'Point', 'source': 'Next target', 'dest': 'Pointing' },
    { 'trigger': 'Acquire', 'source': 'Pointing', 'dest': 'Acquisition' },
    { 'trigger': 'Process', 'source': 'Acquisition', 'dest': 'Processing' },
    { 'trigger': 'Loop', 'source': 'Processing', 'dest': 'Next target' },
    { 'trigger': 'Park', 'source': ['Next target', 'Pointing', 'Acquisition', 'Processing'], 'dest': 'Parking' },
    { 'trigger': 'Sleep', 'source': 'Parking', 'dest': 'Standby' }
]

	def __init__(self, name):

		self.name = name
		NextTarget = self.NextTarget
		# DataBase = self.DataBase

		# Initialize the state machine
		self.machine = Machine(model=self, states=self.states, transitions=self.transitions, initial='Standby')

	def start_obs(self):
		self.Open()
		
	def start_open(self):
		print(f">> Current state: {self.state}")
		print(f"Shelter Opening time - 3s.")
		time.sleep(1.5)
		print("Shelter now open.")
		self.DefineTarget()

	def start_next_target(self):
		print(f">> Current state: {self.state}")
		self.NextTarget = DefineNextTarget()
		# ~ self.NextTarget.display()
		self.Point()
		
	def start_pointing(self):
		print(f">> Current state: {self.state}")
		ra = self.NextTarget.RA
		dec = self.NextTarget.DEC
		print(f"Target coordinates: ra:{ra}, dec:{dec}")
		TargetCoord = SkyCoord(ra, dec, frame='icrs')
		PointScope(TargetCoord)
		TargetCorrectedCoord = TargetCoordinatesCorrection(TargetCoord)
		PointScope(TargetCorrectedCoord)
		# ~ print("Pointage terminé")
		self.Acquire()
		
	def start_acquisition(self):
		print(f">> Current state: {self.state}")
		TakeSeriesGuidingImage(self.NextTarget.MyName, 1, "FRAME_LIGHT", 3.0)
		self.Process()
		
	def start_processing(self):
		print(f">> Current state: {self.state}")
		if (Prog.NbRemaining() > 0):
			self.Loop()
		else:
			self.Park()

	def start_parking(self):
		print(f">> Current state: {self.state}")
		self.Sleep()
		exit

class ObservingProgram():
	Targets = ["Vega", "Albireo", "sheliak", "Alpheratz"]
	# ~ Targets = ["Vega", "Alpheratz"]
	Index = 0
	MaxIndex = len(Targets)
	
	def NextObject(self):
		if (self.Index < self.MaxIndex):
			NextObj = self.Targets[self.Index]
			self.Index += 1
			return NextObj
		else:
			return "No more"
	
	def NbRemaining(self): # Renvoie le nb de cibles restantes
		return (self.MaxIndex - self.Index)

def DefineNextTarget():
	# Cette fonction est à enrichir !
	DataBase = TargetBase()
	if (Prog.NbRemaining() > 0):
		Object = Prog.NextObject()
		print(Object)
		Nb, NextTarget = DataBase.query_get(Object)
	else:
		NextTarget = ""
	# Penser à vérifier qu'il n'y a qu'un seul résultat...
	return(NextTarget)
	
def TargetCoordinatesCorrection(TargetCoord):
	'''This functions calculates the cordinates to put the target in the slit (instead of the image center).'''
	print(f"Coordonnées : {TargetCoord}")
	# On teste le côté du pilier
	PierSide = mount.get_pier_side()
	print(f"{PierSide}...")
	if (PierSide['PIER_WEST'] == "On"):
		# ~ TargetCorrectedCoord = TargetCoord.spherical_offsets_by(SlitOffsetRA, SlitOffsetDEC) # already given in *u.arcmin
		TargetCorrectedCoord = TargetCoord.spherical_offsets_by(-SlitOffsetRA, SlitOffsetDEC) # already given in *u.arcmin		
	else:
		# ~ TargetCorrectedCoord = TargetCoord.spherical_offsets_by(SlitOffsetRA, SlitOffsetDEC) # already given in *u.arcmin
		TargetCorrectedCoord = TargetCoord.spherical_offsets_by(-SlitOffsetRA, -SlitOffsetDEC) # already given in *u.arcmin		
	print(f"Coordonnées corrigées : {TargetCorrectedCoord}")
	return TargetCorrectedCoord
	
def PointScope(TargetCoord):
    # Starting coordinates
    c_true = mount.get_current_coordinates()
    print("BEFORE SLEWING --------------------------")
    print(f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}")

    print("SLEWING ---------------------------------")
    mount.slew_to_coord_and_track(TargetCoord)
    print("After SLEWING --------------------------")
    print(f"Coordinates are now: ra:{TargetCoord.ra.to(u.hourangle)}, dec:{TargetCoord.dec.to(u.degree)}")

def TakeSeriesGuidingImage(Target, Number, FrameType, ExpTime):
	# Get current ISO 8601 datetime in string format
	Now_ISO_UTC = datetime.now(timezone.utc).isoformat()
	# ~ print('ISO DateTime:', Now_ISO_UTC)
	GenericFileName = SessionFolder + "/" + UniqueRootFileName(Now_ISO_UTC, Target, FrameType, ExpTime)
	for Index in range(Number):
		TakeOneGuidingImage(Target, GenericFileName, Index+1, FrameType, ExpTime)
		
def TakeOneGuidingImage(Target, GenericName, Index, Type, Exposure):
    print("---> Take a guiding image.")

    # set frame type (mostly for simulation purpose
    camGuidage.set_frame_type(Type)
    
    # Acquire image Guidage
    camGuidage.prepare_shoot()
    camGuidage.setExpTimeSec(Exposure)
    camGuidage.shoot_async()
    camGuidage.synchronize_with_image_reception()
    fitsGuidage = camGuidage.get_received_image()
    
    # Je remplis
    fitsGuidage[0].header['OBJECT'] = Target
    Object = fitsGuidage[0].header['OBJECT']
    # ~ print(f"Objet : {Object}")

    FitsFileName = GenericName + str(Index) + ".fits"
    print(f"File name: {FitsFileName}")
    fitsGuidage.writeto(FitsFileName)

    # ~ PNGFileName = FileName + ".png"
    # ~ print(f"Fichier sauvé : {PNGFileName}")
    # ~ plt.savefig(PNGFileName, format="png")

    # ~ PdfFileName = FileName + ".pdf"
    # ~ print(f"Fichier sauvé : {PdfFileName}")
    # ~ plt.savefig(PdfFileName, format="pdf")    

    # Show images
    # fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(16, 9))
    # ~ fig, ((ax1, ax2)) = plt.subplots(nrows=1, ncols=2, figsize=(16, 9))
    # ~ imgGuide = fitsGuidage[0].data
    # ~ img_eqGuide = exposure.equalize_hist(imgGuide)
    # ~ print_ready_imgGuide = img_as_float(img_eqGuide)
    # ~ ax1.imshow(print_ready_imgGuide, cmap='gray')
    # plt.show()

def SetSessionFolder(Instrument):
	# This function defines the Session Folder - and create it if it does'nt exist yet
	base = "/media/observatoire/TR-002-Astro/"
	# In the HDD, we've one folder per year
	currentYear = str(date.today().year)
	YearFolder = "Observations-" + currentYear + "/"
	# Now, we create the actual session folder
	now = datetime.now()
	HourNow = now.hour
	# We consider that a night session starts at noon and finishes at noon the day after
	if (HourNow > 12):
		SessionDate = date.today()
	else:
		SessionDate = date.today() + timedelta(days=-1)
	Day = str(SessionDate.year) + str(SessionDate.month) +str(SessionDate.day)
	FolderName = base + YearFolder + Day + "-AutoObs-" + Instrument
	# We create the directory if it does not exist
	if not os.path.exists(FolderName):
		os.makedirs(FolderName)
		print(f"Creation of the session folder: {FolderName}")
	else:
		print(f"Session folder already existing: {FolderName}")
	return(FolderName)
	
def UniqueRootFileName(DateObs, Target, FrameType, ExpTime):
	DateObs = ExtractDateObs(DateObs) # To adapt the date-time format to a file name
	FileName = Target.replace(" ", "") + "-" + FrameType + "-" + str(int(ExpTime)) + "s-" + DateObs +"-" 
	return FileName
	
def ExtractDateObs(DateObs):
	"""Extract the Date & time from DATEOBS Fits keyword, for unique file name creation. DATEOBS is like '2022-10-20T16:41:04.749'. Result is '20221020T164104'."""
	DatetimeStr = DateObs.split('.')[0] # To remove decimals in the seconds (no need for such a precision)
	DatetimeStr = DatetimeStr.replace('-', '') # To remove '-' in date
	DatetimeStr = DatetimeStr.replace(':', '') # To remove ':' in time
	return DatetimeStr
	
def FetchRefGuidingImage():
	'''Copies the guiriding reference image to the working directory'''
	base = "/media/observatoire/TR-002-Astro/Reference-images/Guiding/"	
	FileName = "HD153344.fits"
	File = base + FileName
	if (os.path.exists(File)):
		return File
	else:
		return "Toto.fits"
	
def MeasureSlitOffsets(SlitSkyImageRef, SlitCenterX, SlitCenterY):
	'''Measures the RaDec offset of the slit center vs Guiding image center. Based on a Reference image (taken in a previous observation).'''
	RefGuidingFile = FetchRefGuidingImage()
	print(f"Firchier de ref : {RefGuidingFile}")
	hdu_list = fits.open(RefGuidingFile)
	header = hdu_list[0].header
	w = WCS(header)

	CenterPixX = int(header['NAXIS1'] /2)
	CenterPixY = int(header['NAXIS2'] /2)
	print(f"Centre (pixels) : {CenterPixX}, {CenterPixY}")
		
	CenterSkyX, CenterSkyY = w.wcs_pix2world(CenterPixX, CenterPixY, 1)
	Center = SkyCoord(CenterSkyX, CenterSkyY, frame='icrs', unit='deg')
	print(f"Coords centre image direct : {Center}")
	print(f"Coords centre image : {Center.to_string('hmsdms')}")
	
	SlitSkyX, SlitSkyY = w.wcs_pix2world(SlitCenterX, SlitCenterY, 1)
	Slit = SkyCoord(SlitSkyX, SlitSkyY, frame='icrs', unit='deg')
	print(f"Coords slit: {Slit}")
	print(f"Coords slit: {Slit.to_string('hmsdms')}")
	
	dra, ddec = Center.spherical_offsets_to(Slit)
	# ~ PierSide = mount.get_pier_side()
	# We must take the pier side into account
	# ... à vérifier... peut-être que ce n'est pas à prendre en compte à ce stade ??
	PierSide = header['PIERSIDE']
	print(f"Pilier : {PierSide}")
	# ~ if (PierSide == "EAST"):
		# ~ dra = -dra # A confirmer dans la durée... dépend du côté du méridien ? 
	# ~ else:
		# ~ ddec = -ddec # A confirmer dans la durée... dépend du côté du méridien ? 		
	print(f"Delta RA direct : {dra}") 
	print(f"Delta DEC direct : {ddec}") 
	print(f"Delta RA : {dra.to(u.arcmin)}") 
	print(f"Delta DEC : {ddec.to(u.arcmin)}") 
	return dra, ddec

#---------------------------------------
# Program start
#---------------------------------------

RunMode = "" # To define the actual mode (simu or real)

if (len(sys.argv) == 2):
	if (sys.argv[1] == "simu"):
		# We run the simulation mode (local Kstars Indi server)
		RunMode = "simu"
		print("Run in mode SIMULATOR (run Kstars with simulators config)")
	if (sys.argv[1] == "real"):
		RunMode = "real"
		print("Run in mode REAL (make sure remote Indi server is running)")
if (RunMode == ""):
	print("Requires an argument: 'real' to run in real environment or 'simu' to run in simulator mode.")
	print("In 'real' mode, make sure the remote INDI server is running.")
	print("In 'simu' mode, make sure the local INDI server is running.")
	exit()

# Defines the session folder
SessionFolder = SetSessionFolder("TestGuidage")

# Starts the observing program
Prog = ObservingProgram()
	
# Configuration du serveur INDI
if (RunMode == "simu"):
	indi_config = {
		"indi_host": "localhost",
		"indi_port": 7624
		}
	mount_config = {
		"mount_name": "Telescope Simulator",
		"indi_client": indi_config
		}
	configGuidage = dict(
		autofocus_seconds=5,
		pointing_seconds=5,
		autofocus_size=500,
		indi_client = indi_config,
		camera_name = 'CCD Simulator')
	camGuidage = IndiCamera(config=configGuidage, connect_on_create=False)
	# Define the shift of the slit in the guiding image
	SlitSkyImageRef = "HD153344.fits" # A reference guiding image (made with the same setup as the whole session), with WCS keywords (= made on the sky)
	SlitFlatImageRef = "HD153344.fits" # A reference guiding image (flat or calib, for instance), in which we can measure the X,Y position of the slit center
	# ~ SlitCenterX = 947 # in pixels
	# ~ SlitCenterY = 689 # in pixels
	SlitCenterX = 400 # in pixels
	SlitCenterY = 1000	 # in pixels
	# ~ SlitCenterX = 968 # in pixels
	# ~ SlitCenterY = 608	 # in pixels	SlitOffsetRA = 0.0 # in Arcmin - will be calculated from ref images
	SlitOffsetRA = 0.0 # in Arcmin
	SlitOffsetDEC = 0.0 # in Arcmin - will be calculated from ref images
	
if (RunMode == "real"):
	indi_config = {
		"indi_host": "192.168.144.32",
		"indi_port": 7624
		}
	mount_config = {
		"mount_name": "10micron",
		"indi_client": indi_config
		}
	configGuidage = dict(
		autofocus_seconds=5,
		pointing_seconds=5,
		autofocus_size=500,
		indi_client = indi_config,
		camera_name = 'ZWO CCD ASI174MM Mini')
	camGuidage = IndiZwoASI174MiniCamera(config=configGuidage, connect_on_create=False)
	# Define the shift of the slit in the guiding image
	SlitSkyImageRef = "HD153344.fits" # A reference guiding image (made with the same setup as the whole session), with WCS keywords (= made on the sky)
	SlitFlatImageRef = "HD153344.fits" # A reference guiding image (flat or calib, for instance), in which we can measure the X,Y position of the slit center
	SlitCenterX = 950 # in pixels
	SlitCenterY = 689 # in pixels
	# ~ SlitCenterX = 400 # in pixels
	# ~ SlitCenterY = 1000	 # in pixels
	# ~ SlitCenterX = 968 # in pixels
	# ~ SlitCenterY = 608	 # in pixels	SlitOffsetRA = 0.0 # in Arcmin - will be calculated from ref images
	SlitOffsetRA = 0.0 # in Arcmin
	SlitOffsetDEC = 0.0 # in Arcmin - will be calculated from ref images
	
indi_cli = IndiClient(config=indi_config)

mount = Indi10micronMount(config=mount_config)
mount.unpark()

SlitOffsetRA, SlitOffsetDEC = MeasureSlitOffsets(SlitSkyImageRef, SlitCenterX, SlitCenterY)

camGuidage.connect()
    
Obs = Observations("St-Pancrasse")
# ~ print(f">> Current state: {Obs.state}")
# ~ machine = GraphMachine(model=Obs, states=Observations.states, transitions=Observations.transitions, initial=Obs.state)
# ~ Obs.get_graph().draw("test.png", prog='dot')

Obs.start_obs()


