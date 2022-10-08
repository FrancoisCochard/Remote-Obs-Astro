#!/usr/bin/env python3

'''
Création d'une base de données sqlite pour héberger les cibles à observer
F. Cochard, 04/10/2022
'''

import sqlite3
import os
from Target.Target import Target

class TargetBase():
	
	DataBase = os.path.expanduser("~/Obs-St-Pancrasse/INDI-Python/Remote-Obs-Astro/TargetDatabase/TargetBase.db")

	def query_get(self, Name):
		tdb = sqlite3.connect(self.DataBase)
		cursor = tdb.cursor()
		T = Target()
		request = "SELECT TargetID FROM Alias WHERE AliasName = '" + Name + "' COLLATE NOCASE"
		result = cursor.execute(request)
		res = result.fetchall()
		if (len(res) == 0): # No result
			cursor.close()
			return(0, T)
		if (len(res) == 1): # One result, OK
			TargetID = str(res[0][0])
			request = "SELECT * FROM Targets WHERE TargetID = '" + TargetID + "'"
			result = cursor.execute(request)
			res = result.fetchone()
			T.MyName = Name
			T.SimbadName = res[1]
			T.RA = res[2]
			T.DEC = res[3]
			T.Magnitude = res[4]
			T.SpectralType = res[5]
			T.Extended = "TBD"
			T.Moving = "TBD"
			T.Select = res[8]
			T.Priority = res[9]
			cursor.close()
			return(1, T)
	
	def query_add(self, TargetData):
		tdb = sqlite3.connect(self.DataBase)
		cursor = tdb.cursor()
		T = Target()
		Name = TargetData.SimbadName # To check if the star is already in the local database
		RA = TargetData.RA
		DEC = TargetData.DEC
		Mag = TargetData.Magnitude
		Sp = TargetData.SpectralType
		request = "SELECT TargetID FROM Targets WHERE SimbadName = '" + Name + "' COLLATE NOCASE"
		result = cursor.execute(request)
		res = result.fetchall()
		if (len(res) == 0): # The alias is not known in local database
			print("The Object is unknown in the local database. We add it.")
			request = '''INSERT INTO Targets
				(SimbadName, RA, DEC, Magnitude, SpectralType) 
				VALUES 
				(?, ?, ?, ?, ?)
				'''
			result = cursor.execute(request, (Name, RA, DEC, Mag, Sp))
			tdb.commit()
		print("We add an alias name.")
		request = "SELECT TargetID FROM Targets WHERE SimbadName = '" + Name + "' COLLATE NOCASE"
		result = cursor.execute(request)
		res = result.fetchall()
		TargetID = str(res[0][0])
		AliasName = TargetData.MyName
		request = "INSERT INTO Alias (TargetID, AliasName, Simbad) VALUES (" + TargetID + ", '" + AliasName + "', 0)"
		result = cursor.execute(request)
		tdb.commit()
		cursor.close()
		print(f"The new name is added in the local database (ID : {TargetID}.\n------\n")
