from transitions import Machine

class Matter(object): 
    pass 
 
lump = Matter()

transitions = [
    { 'trigger': 'melt', 'source': 'solid', 'dest': 'liquid' }, 
    { 'trigger': 'evaporate', 'source': 'liquid', 'dest': 'gas' }, 
    { 'trigger': 'sublimate', 'source': 'solid', 'dest': 'gas' }, 
    { 'trigger': 'ionize', 'source': 'gas', 'dest': 'plasma' } 
] 

machine = Machine(model=lump, states=['solid', 'liquid', 'gas', 'plasma'], initial='solid', transitions=transitions) # model_attribute='my_state')

print(lump.state)
