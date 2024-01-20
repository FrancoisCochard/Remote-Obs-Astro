#!/usr/bin/python3

# Test rapide autour des dictionnaires - 16 janvier 2024
# dans la perspective de remplacer la classe passée à la séquence d'observation par un dictionnaire

# D = {'Observatory': {}, 'Devices': {}, 'Observation': {}}

# D['Observatory'] = {'ValA': 10, 'valB': 'OK'}
# print(D.items())
# for A in D.items():
#     print('Là : ', A)
# print(D['Observatory'])

# print(list(D))
# print(D['Observatory']['ValA'])

class F():
    a = 12
    b = 16
    print("Hello...")

class G():
    c = 2
    f = 4

Dict = {'Prem':'F', 'Deuz': 'G'}

# print(Dict)
# print(Dict['Prem'])

eval(Dict['Prem']+'()')
print("OK !")