#!/usr/bin/env python3

'''
FillDatabase.py : script pour alimenter la base de données SQLite à partir des données Simbad
F. Cochard, première version 04/10/2022
Mon intention est d'avoir un petit outil simple pour mettre dans la base de données d'étoiles les données piochées dans Simbad
'''

from Target.Target import Target
from TargetDatabase.TargetBase import TargetBase # Je charge la base de données
import cmd # Command line lib
from astroquery.simbad import Simbad
import warnings # To ingnore the Apstropy warnings
from astropy import units as u
from astropy.coordinates import SkyCoord

class TargetShell(cmd.Cmd):
	intro = 'Welcome to Target shell. Type help or ? to list commands.\n'
	prompt = '->'
	
	def SimbadRequest(self, Name):
		"""To request Simbad"""
		result_table = Sq.query_object(Name)
		if (result_table is None):
			Nb = 0
		else:
			Nb = 1
			coordinates = result_table["RA"][0] + " " + result_table["DEC"][0]
			C = SkyCoord(coordinates, unit=(u.hourangle, u.deg)) # Pour formater les coordonnées en hms & dms
			T.MyName = Name
			T.SimbadName = result_table["MAIN_ID"][0]
			T.RA = C.to_string('hmsdms').split()[0] # Pour formater les coordonnées en hms
			T.DEC = C.to_string('hmsdms').split()[1] # Pour formater les coordonnées en dms
			T.Magnitude = result_table["FLUX_V"][0]
			T.SpectralType = result_table["SP_TYPE"][0]
			T.Extended = ""
			T.Moving = ""
			T.Select = ""
			T.Priority = "T"			
		return(Nb, T)

	# Commands definition
	def do_simbad(self, targetName):
		'request a name to Simbad (no other action). Give target name as argument (ie "simbad Vega")'
		Nb, T = self.SimbadRequest(targetName)
		if (Nb == 1):
			print("The star is known by Simbad.\n--------")
			T.display()
		else:
			print(f"NO result found in Simbad.\n--------\n")		
		
	def do_bye(self, arg):
		'bye - to quite the Target Shell program.'
		print('End of the Target Shell.\nGoodbye!')
		quit()
		
	def do_get(self, targetName):
		'To get data from a target from its name.'
		Nb, Result = Tdb.query_get(targetName)
		if (Nb == 1):
			print("The star already exists in the local database.\n--------")
			Result.display()
		else:
			print("The star is NOT in the local database.\n--------\n")
			
	def do_add(self, targetName):
		'To add a star into the database.'
		Nb, Result = Tdb.query_get(targetName)
		if (Nb == 1):
			print("The star already exists in the local database.\n--------")
			Result.display()
		else: # The star is not in the db yet. Must be added.
			Nb, T = self.SimbadRequest(targetName)			
			if (Nb == 0):
				print("This name is NOT known in Simbad.\n--------\n")
				return
			else:
				SimbadName = T.SimbadName
				print(f"The name is in Simbad: {SimbadName}.")
				Tdb.query_add(T)
		
		
if __name__ == "__main__":
	warnings.filterwarnings('ignore', category=DeprecationWarning, append=True) # To ingnore the Apstropy warnings
	warnings.filterwarnings('ignore', category=UserWarning, append=True) # To ingnore the Apstropy warnings

	T = Target()
	Tdb = TargetBase()
	
	Sq = Simbad()
	Sq.add_votable_fields('sptype', 'flux(V)')
	
	TargetShell().cmdloop()
