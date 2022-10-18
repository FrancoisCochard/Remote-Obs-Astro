from transitions import Machine
from transitions.extensions import GraphMachine

class Matter(object):
    pass

lump = Matter()

a = 12

# ~ from transitions import Machine
# ~ machine = Machine(model=lump, states=['solid', 'liquid', 'gas', 'plasma'], initial='solid')

# The states
states=['solid', 'liquid', 'gas', 'plasma']

# And some transitions between states. We're lazy, so we'll leave out
# the inverse phase transitions (freezing, condensation, etc.).
transitions = [
    { 'trigger': 'melt', 'source': 'solid', 'dest': 'liquid' },
    { 'trigger': 'evaporate', 'source': 'liquid', 'dest': 'gas' },
    { 'trigger': 'sublimate', 'source': 'solid', 'dest': 'gas' },
    { 'trigger': 'ionize', 'source': 'gas', 'dest': 'plasma' }
]

# Initialize
machine = Machine(model=lump, states=states, transitions=transitions, initial='liquid')

# ~ m = Model()
# without further arguments pygraphviz will be used
# ~ m = GraphMachine(model=lump)
# ~ # when you want to use graphviz explicitly
# ~ machine = GraphMachine(model=m, use_pygraphviz=False, ...)
# ~ # in cases where auto transitions should be visible
# ~ machine = GraphMachine(model=m, show_auto_transitions=True, ...)

# draw the whole graph ...
# ~ m.get_graph().draw('my_state_diagram.png', prog='dot')
# ... or just the region of interest
# (previous state, active state and all reachable states)
# ~ roi = m.get_graph(show_roi=True).draw('my_state_diagram.png', prog='dot')


if __name__ == "__main__":
    print("... Machin à propos de main()")
