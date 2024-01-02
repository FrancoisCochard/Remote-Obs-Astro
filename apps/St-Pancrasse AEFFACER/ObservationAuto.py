#!/usr/bin/env python3

'''
ObservationAuto.py : script de base pour automatiser l'observation d'une étoile
F. Cochard, première version 04/10/2022
Mon intention est de mettre en place un script simple qui exploite les briques de base :
- Définition de la cible à pointer
- Récupérer les infos de cette cible dans la base de données (RA, DEC, Nom...)
- Pointer l'étoile DANS LA FENTE
- ACtiver l'autoguidage
- Lancer une série d'acquisitions
... et ensuite on pourra élaborer !

Mon idée première est de mettre en oeuvre les modules (à développer) TargetBase.py et Target.py
'''

# Import de la classe Target depuis le module Target/Target.py
from Scheduler.Target import Target
import Scheduler.TargetBase # pour le moment, je n'ai pas de classe dans ce module, alors je charge direct le module
	
if __name__ == "__main__":
    print("Je lance le script...")
    T = Target("Toto")
    print(T.MyName)

