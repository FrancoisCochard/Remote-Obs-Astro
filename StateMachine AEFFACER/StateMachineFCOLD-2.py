# State Machine for managing the observatory
# F. Cochard, October 2023
# Rev 0.01 Oct. 29th, 2023 : initial version
#
#
# A faire :
# - Passer toute la machine d'état dans la classe ObsStateMachine (pour le moment, la machine est minimale, et toutes les fonctions sont externes)
# - Compléter les API Rest ?
# - Mieux comprendre l'utilité des triggers (je ne fonctionne qu'avec les commandes to_...)
# - Mieux distinguer les fonctions de transition d'un état à l'autre (listées dans les States), et les commandes externes
# - Mettre en place une boucle qui surveille l'état des quelques variables principales (ACTIVATED, NIGHT, GOOD_WEATHER, TARGET_AVAILABLE).
#      >> Note : pour l'instant ce sont des variables artificielles. A terme il faut les remplacer par des fonctions qui vont chercher la véritable info
# - Comprendre d'où viennent tous les messages de log :
# ~ 2023-10-29 07:15:18 - transitions.core -    INFO - Executed callback '<function open_shelter at 0xffffb1814670>'
# ~ 2023-10-29 07:15:18 - transitions.core -    INFO - Finished processing state Opening_dome enter callbacks.
# ~ 2023-10-29 07:15:18 - transitions.core -   DEBUG - Executed callback after transition.
# ~ 2023-10-29 07:15:18 - transitions.core -   DEBUG - Executed machine finalize callbacks
# ~ 2023-10-29 07:15:18 - transitions.core -    INFO - Executed callback '<function is_target_available at 0xffffb18145e0>'
# ~ 2023-10-29 07:15:18 - transitions.core -    INFO - Finished processing state Wait_target enter callbacks.
# ~ 2023-10-29 07:15:18 - transitions.core -   DEBUG - Executed callback after transition.
# ---------------------------------------------

from transitions import Machine, State
from time import sleep
from random import *
import sys, os
sys.path.append( os.path.join( os.path.dirname(os.path.realpath(__file__)), ".." ) )

import uvicorn
from dependencies import settings, initLogger

logger = initLogger("observatory")
print("LOGGER : ", logger)

class ObsStateMachine(object):
    
    # Variables pour tester la machine (à supprimer à terme ?)
    ACTIVATED = True
    NIGHT = True
    GOOD_WEATHER = True
    TARGET_AVAILABLE = True
    
    def __init__(self):
        pass

def Obs_State():
    return Obs.state

def startup_process():
    logger.info( "TEST de message (startup) : on démarre la machine d'état" )
    # Function launched at startup. Note: cannot be an 'on_enter' function, because initialisation is the initial step
    Obs.to_Deactivated()

def is_it_activated():
    print("Activated : ", Obs.ACTIVATED)
    if Obs.ACTIVATED == True :
        print("Obs is activated")
        Obs.to_Daylight()
    else:
        print("Obs NOT activated")        

def is_night_OK():
    print("Night : ", Obs.NIGHT)
    if Obs.NIGHT == True :
        print("Night is here")
        Obs.to_Wait_weather()
    else:
        print("Still daylight")        

def is_weather_OK():
    print("Weather OK : ", Obs.GOOD_WEATHER)
    if Obs.GOOD_WEATHER == True :
        print("Weather is OK")
        Obs.to_Wait_target()
    else:
        print("Weather NOT OK")        

def is_target_available():
    print("Target available : ", Obs.TARGET_AVAILABLE)
    if Obs.TARGET_AVAILABLE == True :
        print("We can start observations")
        Obs.to_Opening_dome()
    else:
        print("No target at the moment")        

# ~ def is_target_available():
    # ~ print("Target available : ", Obs.TARGET_AVAILABLE)
    # ~ return Obs.TARGET_AVAILABLE
        
def open_shelter():
    print("State : ", Obs.state)
    print("J'ouvre l'Obs. Trouver la commande API Rest à lancer")
    # Définir comment fermer l'observatoire


def shelter_is_open():
    print("State : ", Obs.state)
    print("Je viens de recevoir l'info que l'observatoire est ouvert")
    if Obs.state == "Opening_dome" :
        Obs.to_Next_target()

def look_for_target():
    print("State : ", Obs.state)
    # On doit ici faire appel au scheduler. En attendant :
    # ---------------------------
    Cible = ["Vega", "Arcturus", "Deneb", "gam Cas", "rho Oph", "ome Ori", "Fin"]
    Target = choice(Cible)
    print("Prochaine cible : ", Target)
    # ---------------------------
    if Target == "Fin" :
        print("Fin des observations")
        Obs.TARGET_AVAILABLE = False
        Obs.to_Closing_dome()
    else :
        print("Observation : ", Target)
        Obs.to_Observation(Target)

def start_observation(Target):
    print("State : ", Obs.state)
    print("Démarrage de l'observation de ", Target)
    # Définir comment lancer l'observation

def observation_is_done(Target):
    print("State : ", Obs.state)
    print("Fin de l'observation de ", Target)
    if Obs.state == "Observation" :
        Obs.to_Next_target()

def close_shelter():
    print("Je ferme l'Obs.")
    print("State : ", Obs.state)
    # Définir comment fermer l'observatoire

def shelter_is_closed():
    print("L'observatoire est fermé")
    print("State : ", Obs.state)
    if Obs.state == "Closing_dome" :
        Obs.to_Deactivated() # We come back at the process start-up

def activate_observatory():
    print("State : ", Obs.state)
    print("Activation de l'observatoire : ", Target)
    ACTIVATED = True
    if Obs.state == "Deactivated" :
        Obs.to_Daylight()

def target_available():
    print("State : ", Obs.state)
    print("A target is now available")
    TARGET_AVAILABLE = True
    if Obs.state == "Wait_target" :
        Obs.to_Deactivated() # We come back at the process start-up

def weather_is_OK():
    print("State : ", Obs.state)
    GOOD_WEATHER = True
    print("Weather is OK")
    if Obs.state == "Wait_weather" :
        Obs.to_Deactivated() # We come back at the process start-up

def weather_is_BAD():
    print("State : ", Obs.state)
    GOOD_WEATHER = False
    print("Weather is BAD")
    if (Obs.state == "Opening_dome" or Obs.state == 'Next_target') :
        Obs.Closing_dome()
    if (Obs.state == "Observation") :
        # Stop observation... voir comment je fais
        observation_is_done("Je termine prématurément l'observation")

# ~ def Open_dome():
    # ~ pass

states = [
    State(name='Initialization'),
    State(name='Deactivated', on_enter=[is_it_activated]),
    State(name='Daylight', on_enter=[is_night_OK]),
    State(name='Wait_weather', on_enter=[is_weather_OK]),
    State(name='Wait_target', on_enter=[is_target_available]),
    # ~ State(name='Wait_target', on_enter=[Open_dome]),
    State(name='Opening_dome', on_enter=[open_shelter]),
    State(name='Next_target', on_enter=[look_for_target]),
    State(name='Observation', on_enter=[start_observation]),
    State(name='Closing_dome', on_enter=[close_shelter]),
    ]
    
# ~ transitions = [
    # ~ { 'trigger': 'locking', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'unlocking', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'daylight', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'night', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'good_weather', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'Deactivate_obs', 'source': 'Closing_dome', 'dest': 'Deactivated' },
    # ~ { 'trigger': 'Activate_obs', 'source': 'Deactivated', 'dest': 'Daylight' },
    # ~ { 'trigger': 'Open_dome', 'source': 'Wait_target', 'dest': 'Opening_dome' }
    # ~ ]

Obs = ObsStateMachine()
# ~ machine = Machine(Obs, states=states, transitions=transitions, initial='Initialization')
machine = Machine(Obs, states=states, initial='Initialization')
logger.info( "On a démarré" ) 
