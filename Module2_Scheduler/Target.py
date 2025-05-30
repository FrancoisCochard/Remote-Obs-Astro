#!/usr/bin/env python3

'''
Target.py : définition de la classe Target
'''

# La position est donnée par un objet SkyCoord...

class Target:
	"""Target class"""
	def __init__(self, MyName="", SimbadName="", RA="", DEC="", Magnitude=100, SpectralType="None", Extended=False, Moving=False, Select=False, Priority=0):
		self.MyName = MyName
		self.SimbadName = SimbadName
		self.RA = RA
		self.DEC = DEC
		self.Magnitude = Magnitude
		self.SpectralType = SpectralType
		self.Extended = Extended
		self.Moving = Moving
		self.Select = Select
		self.Priority = Priority
	
	def display(self):
		print(f'Target Name: {self.MyName}')
		print(f'Simbad Name: {self.SimbadName}')
		print(f'RA: {self.RA}')
		print(f'DEC: {self.DEC}')
		print(f'Magnitude: {self.Magnitude}')
		print(f'Spectral type: {self.SpectralType}')
		print(f'Extended: {self.Extended}')
		print(f'Moving: {self.Moving}')
		print(f'Select: {self.Select}')
		print(f'Priority: {self.Priority}')
		
if __name__ == "__main__":
    print("... Machin à propos de main()")
    # ~ T = Target("Toto")
    # ~ print(T.MyName)
