#!/usr/bin/python3

# Test rapide autour des dictionnaires - 16 janvier 2024
# dans la perspective de remplacer la classe passée à la séquence d'observation par un dictionnaire

D = {'Observatory': {}, 'Devices': {}, 'Observation': {}}

D['Observatory'] = {'ValA': 10, 'valB': 'OK'}
print(D.items())
for A in D.items():
    print('Là : ', A)
print(D['Observatory'])

print(list(D))
print(D['Observatory']['ValA'])
