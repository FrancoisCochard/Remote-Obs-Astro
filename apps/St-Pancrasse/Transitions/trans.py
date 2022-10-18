from transitions import Machine, State
from transitions.extensions import GraphMachine
from Target.Target import Target
from TargetDatabase.TargetBase import TargetBase # Je charge la base de données
from helper.IndiClient import IndiClient
from Mount.Indi10micronMount import Indi10micronMount
from astropy import units as u
from astropy.coordinates import SkyCoord
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
from datetime import date, datetime, timedelta

class Observations(object):
	
	NextTarget = Target()

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
		self.NextTarget.display()
		self.Point()
		
	def start_pointing(self):
		print(f">> Current state: {self.state}")
		PointScope(self.NextTarget)
		time.sleep(1.5)
		print("Pointage terminé")
		self.Acquire()
		
	def start_acquisition(self):
		print(f">> Current state: {self.state}")
		AcquireGuiding(3.0)
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
	Targets = ["Vega", "om Her", "tet Lyr", "Albireo", "sheliak"]
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
		# ~ Nb, NextTarget = DataBase.query_get("Vega")
		print(Nb, NextTarget)
	else:
		NextTarget = ""
	# Penser à vérifier qu'il n'y a qu'un seul résultat...
	return(NextTarget)

def PointScope(Target):
    # Build the Mount    
    print(f"Monture connectée... {mount.is_connected}")    
    print("Unparking the mount.")
    mount.unpark()

    # Starting coordinates
    c_true = mount.get_current_coordinates()
    print("BEFORE SLEWING --------------------------")
    print(f"Coordinates are now: ra:{c_true.ra.to(u.hourangle)}, dec:{c_true.dec.to(u.degree)}")

    ra = Target.RA
    dec = Target.DEC
    print(f"Target coordinates: ra:{ra}, dec:{dec}")
    c = SkyCoord(ra, dec, frame='icrs')
    # ~ print(c)
    # ~ print(c.to_string('hmsdms'))
    # ~ print(f"Nouvelle cible: ra:{c.ra.to(u.hourangle)}, dec:{c.dec.to(u.degree)}")
    print("SLEWING ---------------------------------")
    mount.slew_to_coord_and_track(c)
    print("After SLEWING --------------------------")
    print(f"Coordinates are now: ra:{c.ra.to(u.hourangle)}, dec:{c.dec.to(u.degree)}")
    # time.sleep(2); # On attend un peu pour que la monture se stabilise

    # ~ print("Je parke !")
    # ~ mount.park()    
    # ~ print(f"Status parking : {mount.is_parked}")

def AcquireGuiding(Exposure):
    print("\n---> Caméra Guidage")

    # set frame type (mostly for simulation purpose
    camGuidage.set_frame_type('FRAME_LIGHT')
    print("Passé en frame Light")

    # set gain
    # ~ camGuidage.set_gain(100)
    # ~ print(f"gain is {camGuidage.get_gain()}")
    
    # ~ # Profondeur d'image
    # ~ print(f"Depth is {camGuidage.get_frame_depth()}")
    # ~ # Je passe en 16 bits
    # ~ # camGuidage.set_frame_depth(16)
    # ~ camGuidage.set_frame_depth(8)
    # ~ print(f"Depth is now {camGuidage.get_frame_depth()}")
    
    # Acquire image Guidage
    camGuidage.prepare_shoot()
    camGuidage.setExpTimeSec(Exposure)
    camGuidage.shoot_async()

    camGuidage.synchronize_with_image_reception()
    fitsGuidage = camGuidage.get_received_image()
    FileName = SessionFolder + "/" + UniqueFileName("DateObs", Obs.NextTarget.MyName, "Object", 3) + "1"
    FitsFileName = FileName + ".fits"
    print(f"Fichier sauvé : {FitsFileName}")
    PNGFileName = FileName + ".png"
    print(f"Fichier sauvé : {PNGFileName}")
    PdfFileName = FileName + ".pdf"
    print(f"Fichier sauvé : {PdfFileName}")
    #fitsGuidage.writeto('new1.fits', overwrite=True)
    fitsGuidage.writeto(FitsFileName, overwrite=True)

    # Show images
    # fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(16, 9))
    fig, ((ax1, ax2)) = plt.subplots(nrows=1, ncols=2, figsize=(16, 9))
    
    imgGuide = fitsGuidage[0].data
    img_eqGuide = exposure.equalize_hist(imgGuide)
    print_ready_imgGuide = img_as_float(img_eqGuide)
    ax1.imshow(print_ready_imgGuide, cmap='gray')

    #plt.show()
    plt.savefig(PNGFileName, format="png")
    plt.savefig(PdfFileName, format="pdf")    

def SetSessionFolder(Instrument):
	# This function defines the Session Folder - and create it if it does'nt exist yet
	base = "/media/observatoire/Observations/"
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
	
def UniqueFileName(DateObs, Target, FrameType, ExpTime):
	FileName = Target.replace(" ", "") + "-" + FrameType + "-" + str(ExpTime) + "s-" + DateObs +"-" 
	print(FileName)
	return FileName


# Program start
print('To run the script in Simulator mode, run it with argument "simu"')

if (len(sys.argv) == 2):
	# We run the simulation mode (local Kstars Indi server)
	RunMode = "Simu"
	print("Run in mode SIMULATOR (run Kstars with simulators config)")
else:
	RunMode = "real"
	print("Run in mode REAL (make sure remote Indi server is running)")

# A effacer : test local
a = UniqueFileName("20220612T124158", "Vega", "Object", 15)

SessionFolder = SetSessionFolder("TestGuidage")

Prog = ObservingProgram()

# Configuration du serveur INDI
if (RunMode == "Simu"):
	indi_config = {
		"indi_host": "localhost",
		"indi_port": 7624
	}
else: 
	indi_config = {
		"indi_host": "192.168.144.32",
		"indi_port": 7624
	}
# ~ print("Hey...", indi_config)

indi_cli = IndiClient(config=indi_config)

if (RunMode == "Simu"):
	mount_config = {
		"mount_name": "Telescope Simulator",
		"indi_client": indi_config
	}
else: 
	mount_config = {
		"mount_name": "10micron",
		"indi_client": indi_config
	}
# ~ print("Hello...", mount_config)

mount = Indi10micronMount(config=mount_config)

configGuidage = dict(
	autofocus_seconds=5,
	pointing_seconds=5,
	autofocus_size=500,
	indi_client = indi_config)

if (RunMode == "Simu"):
	configGuidage["camera_name"] = 'CCD Simulator'
else: 
	configGuidage["camera_name"] = 'ZWO CCD ASI174MM Mini'

# test indi virtual camera class
if (RunMode == "Simu"):
	camGuidage = IndiCamera(config=configGuidage, connect_on_create=False)
else: 
	camGuidage = IndiZwoASI174MiniCamera(config=configGuidage, connect_on_create=False)

camGuidage.connect()
    
Obs = Observations("St-Pancrasse")
print(f">> Current state: {Obs.state}")
# ~ machine = GraphMachine(model=Obs, states=Observations.states, transitions=Observations.transitions, initial=Obs.state)
# ~ Obs.get_graph().draw("test.png", prog='dot')

Obs.start_obs()

# ~ SessionFolder = SetSessionFolder("UVEX")

