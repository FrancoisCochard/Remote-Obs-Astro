from transitions import Machine, State
from time import sleep

# Variables pour tester la machine (à supprimer à terme)
LOCKED = False

class ObsStateMachine(object):
    pass

    # Define some states. Most of the time, narcoleptic superheroes are just like
    # everyone else. Except for...
    # ~ states = [
        # ~ State(name='Initialization'),
        # ~ State(name='Locked', on_enter=[is_it_locked]),
        # ~ State(name='Daylight', on_enter=[is_night_OK]),
        # ~ State(name='Wait_weather', on_enter=[is_weather_OK]),
        # ~ State(name='Wait_target', on_enter=[is_target_available]),
        # ~ State(name='pening_dome', on_enter=[open_observatory]),
        # ~ State(name='Next_target', on_enter=[look_for_target]),
        # ~ State(name='Observation', on_enter=[start_observation]),
        # ~ State(name='Closing_dome'on_enter=[close_observatory])
        # ~ ]
    # ~ transitions = [
    # ~ { 'trigger': 'locking', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'unlocking', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'daylight', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'night', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'good_weather', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'bad_weather', 'source': '', 'dest': '' },
    # ~ { 'trigger': 'target_available', 'source': '', 'dest': '' }
    # ~ ]

    def __init__(self):
        pass
        # ~ startup_process()


def startup_process():
    # Function launched at startup. Note: cannot be an 'on_enter' function, because initialisation is the initial step
    sleep(3) # En attendant de faire mieux
    Obs.to_Locked()

def is_it_locked():
    global LOCKED
    print("Locked : ", LOCKED)
    sleep(3)
    if LOCKED == False :
        print("Obs NOT locked")
        Obs.to_Closing_dome()
    else:
        print("Obs locked")        
        
def close_observatory():
    global LOCKED
    print("Je ferme l'Obs.")
    print("State : ", Obs.state)
    sleep(2)
    LOCKED = True
    Obs.to_Locked()
    print("State : ", Obs.state)

states = [
    State(name='Initialization'),
    State(name='Locked', on_enter=[is_it_locked]),
    # ~ State(name='Daylight', on_enter=[is_night_OK]),
    # ~ State(name='Wait_weather', on_enter=[is_weather_OK]),
    # ~ State(name='Wait_target', on_enter=[is_target_available]),
    # ~ State(name='pening_dome', on_enter=[open_observatory]),
    # ~ State(name='Next_target', on_enter=[look_for_target]),
    # ~ State(name='Observation', on_enter=[start_observation]),
    State(name='Closing_dome', on_enter=[close_observatory]),
    ]
    
transitions = [
    { 'trigger': 'locking', 'source': '', 'dest': '' },
    { 'trigger': 'unlocking', 'source': '', 'dest': '' },
    { 'trigger': 'daylight', 'source': '', 'dest': '' },
    { 'trigger': 'night', 'source': '', 'dest': '' },
    { 'trigger': 'good_weather', 'source': '', 'dest': '' },
    { 'trigger': 'bad_weather', 'source': '', 'dest': '' },
    { 'trigger': 'target_available', 'source': '', 'dest': '' }
]


Obs = ObsStateMachine()
machine = Machine(Obs, states=states, initial='Initialization')
print("Au départ : ", Obs.state)
startup_process()
print("Ensuite : ", Obs.state)

