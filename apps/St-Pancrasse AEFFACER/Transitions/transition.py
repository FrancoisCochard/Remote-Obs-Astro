from transitions import Machine
# from transitions.extensions import GraphMachine

class Matter(object):
    pass

lump = Matter()


# The states
# states=['solid', 'liquid', 'gas', 'plasma']

# And some transitions between states. We're lazy, so we'll leave out
# the inverse phase transitions (freezing, condensation, etc.).
transitions = [
    { 'trigger': 'melt', 'source': 'solid', 'dest': 'liquid' },
    { 'trigger': 'evaporate', 'source': 'liquid', 'dest': 'gas' },
    { 'trigger': 'sublimate', 'source': 'solid', 'dest': 'gas' },
    { 'trigger': 'ionize', 'source': 'gas', 'dest': 'plasma' }
]

# Initialize
# machine = Machine(model=lump, states=states, transitions=transitions, initial='liquid')
machine = Machine(model=lump, states=['solid', 'liquid', 'gas', 'plasma'], initial='solid')

if __name__ == "__main__":
    print("... Machin à propos de main()")
