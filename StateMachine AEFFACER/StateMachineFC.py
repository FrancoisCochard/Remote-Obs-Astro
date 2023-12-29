# State Machine for managing the observatory
# F. Cochard, October 2023
# Rev 0.01 Oct. 29th, 2023 : initial version
#
#
# A faire :
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
from dependencies import initLogger
from random import choice
import sys, os
sys.path.append( os.path.join( os.path.dirname(os.path.realpath(__file__)), ".." ) )

logger = initLogger("observatory")

class ObsStateMachine(object):
    
    # Variables pour tester la machine (à supprimer à terme ?)
    ACTIVATED = True
    NIGHT = True
    GOOD_WEATHER = True
    TARGET_AVAILABLE = True
    
    def __init__(self):
 
        states = [
        State(name='Initialization'),
        State(name='Deactivated', on_enter=[self.is_it_activated]),
        State(name='Daylight', on_enter=[self.is_night_OK]),
        State(name='Wait_weather', on_enter=[self.is_weather_OK]),
        State(name='Wait_target', on_enter=[self.is_target_available]),
        State(name='Opening_dome', on_enter=[self.open_shelter]),
        State(name='Next_target', on_enter=[self.look_for_target]),
        State(name='Observation', on_enter=[self.start_observation]),
        State(name='Closing_dome', on_enter=[self.close_shelter]),
        ]

        self.machine = Machine(model=self, states=states)
        self.startup_process() # Runs the State Machine

    def Obs_State(self):
        return self.state

    def startup_process(self):
        logger.info( "TEST de message (startup) : on démarre la machine d'état" )
        # Function launched at startup. Note: cannot be an 'on_enter' function, because initialisation is the initial step
        self.to_Deactivated()

    def is_it_activated(self):
        print("Activated : ", self.ACTIVATED)
        if self.ACTIVATED == True :
            print("Obs is activated")
            self.to_Daylight()
        else:
            print("Obs NOT activated")        

    def is_night_OK(self):
        print("Night : ", self.NIGHT)
        if self.NIGHT == True :
            print("Night is here")
            self.to_Wait_weather()
        else:
            print("Still daylight")        

    def is_weather_OK(self):
        print("Weather OK : ", self.GOOD_WEATHER)
        if self.GOOD_WEATHER == True :
            print("Weather is OK")
            self.to_Wait_target()
        else:
            print("Weather NOT OK")        

    def is_target_available(self):
        print("Target available : ", self.TARGET_AVAILABLE)
        if self.TARGET_AVAILABLE == True :
            print("We can start observations")
            self.to_Opening_dome()
        else:
            print("No target at the moment")        
          
    def open_shelter(self):
        print("State : ", self.state)
        print("J'ouvre l'Obs. Trouver la commande API Rest à lancer")
        # Définir comment fermer l'observatoire


    def shelter_is_open(self):
        print("State : ", self.state)
        print("Je viens de recevoir l'info que l'observatoire est ouvert")
        if self.state == "Opening_dome" :
            self.to_Next_target()

    def look_for_target(self):
        print("State : ", self.state)
        # On doit ici faire appel au scheduler. En attendant :
        # ---------------------------
        Cible = ["Vega", "Arcturus", "Deneb", "gam Cas", "rho Oph", "ome Ori", "Fin"]
        Target = choice(Cible)
        print("Prochaine cible : ", Target)
        # ---------------------------
        if Target == "Fin" :
            print("Fin des observations")
            self.TARGET_AVAILABLE = False
            self.to_Closing_dome()
        else :
            print("Observation : ", Target)
            self.to_Observation(Target)

    def start_observation(self, Target):
        print("State : ", self.state)
        print("Démarrage de l'observation de ", Target)
        # Définir comment lancer l'observation

    def observation_is_done(self, Target):
        print("State : ", self.state)
        print("Fin de l'observation de ", Target)
        if self.state == "Observation" :
            self.to_Next_target()

    def close_shelter(self):
        print("Je ferme l'Obs.")
        print("State : ", self.state)
        # Définir comment fermer l'observatoire

    def shelter_is_closed(self):
        print("L'observatoire est fermé")
        print("State : ", self.state)
        if self.state == "Closing_dome" :
            self.to_Deactivated() # We come back at the process start-up

    def activate_observatory(self):
        print("State : ", self.state)
        print("Activation de l'observatoire : ", Target)
        self.ACTIVATED = True
        if self.state == "Deactivated" :
            self.to_Daylight()

    def target_available(self):
        print("State : ", self.state)
        print("A target is now available")
        self.TARGET_AVAILABLE = True
        if self.state == "Wait_target" :
            self.to_Deactivated() # We come back at the process start-up

    def weather_is_OK(self):
        print("State : ", self.state)
        self.GOOD_WEATHER = True
        print("Weather is OK")
        if self.state == "Wait_weather" :
            self.to_Deactivated() # We come back at the process start-up

    def weather_is_BAD(self):
        print("State : ", self.state)
        self.GOOD_WEATHER = False
        print("Weather is BAD")
        if (self.state == "Opening_dome" or Obs.state == 'Next_target') :
            self.Closing_dome()
        if (self.state == "Observation") :
            # Stop observation... voir comment je fais
            self.observation_is_done("Je termine prématurément l'observation")
