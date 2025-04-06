# Quelques questions pendant le développement...

### Fonction Haut Niveau Caméra 

22/12/2023

- Comment je connecte la caméra ? Dans la procédure d'initiation, ou pour chaque image ?
- Comment je définis la température de caméra ? Dans la phase d'initialisation !

> il faut donc que je commence par régler la caméra au début du process d'observation :
> - Connecter la caméra
> - Définir la température
> - Définir le gain et l'offset
> - Le crop ?
> - Mettre l'UVEX en position SKY

Ensuite, pendant l'acquisition elle-même, je dois définir :

> - Vérifier que la caméra est connectée ? 
> - Le temps de pose
> - Le type d'image (target, flat, calib...)
> - 

---

Je remets cette partie, écrite en //...

C'est donc du côté de la machine d'état de 'observatoire qu'il y a deux phases concernées : 

- La phase d'initialisation, qui...
  - ouvre l'abri,
  - démarre les alimentations (IPX800),
  - connecte les devices,
  - les initialise (ex: refroidissement caméra)
- La phase d'observation proprement dite, qui cause aux différents devices.

Donc les devices INDI appartiennent au script qui gère les observations. C'est dès le démarrage de ce script (en mode service) que la déclaration des devices doit être faite.

Se pose alors ici la question du fichier de configuration. Il doit être lu par le même script (et éventuellement relu à la demande). Le fichier config.yaml est dans le répertoire conf_files... il y  est très bien. En fait, je peux le renommer, et lister simplement les devices que je dois déclarer. Je peux donc faire nettement plus simple qu'aujourd'hui !

---

Je commence à comprendre comment est organisé le device Caméra... de fait dans les libs disponibles, il y a deux structures différentes : l'une basée du IndiClient, et l'autre plus complexe héritée de AbstractCamera et de IndiASICamera. Je préfère de loin la première, plus simple, plus compréhensible. Je suppose que c'est le boulot de Thibault, alors que l'autre vien tde Panoptes.

Je veux donc partir de INDIclient, et faire un truc simple : un module Caméra qui fait le strict nécessaire (j'y reviens), et une surcouche pour enregistrer une image FITS. De fait, je crois utile de faire la distinction entre obtenir une image de la caméra et écrire un fichier Fits sur le disque. 

Concernant la caméra, je veux m'en tenir au minimum, et disposer des commandes suivantes :
- Connexion (et déconnexion, et vérif de connexion)
- Teméprature (get et set)
- Gain & offset (get et set)
- Crop (ROI) (get et set)
- Binning (get et set)
- Frame depth (8 ou 16 bits, get et set)
- Frame type (light, dark, bias, calib, flat)... à part que calib n'existe pas...

Je souhaite un device générique pour les caméras ASI, avec ou sans température. Puis une couche supplémentaire avec chaque caméra (soit ASI120 / ASI174 / ASI183, soit Science / Guidage / Ambiance...). Donc un truc du genre IndiASICamera.py, qui ne fait référence qu'à IndiClient.py

Ensuite, je veux comprendre le détail de la séquence d'acquisition (la caméra est spécifique : on lance la pose, et ensuite on peut faire autre chose en attendant le résultat).

De fait, j'ai quelques bricoles à voir avec Thibault :

1. je veux comprendre à partir de quel fichier Caméra je dois repartir. Est-ce que je peux uniquement m'appuyer sur IndiCamera.py ? Visiblement, toutes les déclinanisons sont des empilages de différentes versions... quid a AbstractCamera ? 

2. Ok pour faire une camera générique ASI (avec ou sans cooling), et déclarer ensuite 4 caméras différentes ? 

3. Comprendre la séquence d'acquisiton complète d'une image (je fais comment pour attendre que l'acquisition soit terminée ?). Est-ce que j'utilise un callback, ou bien je dois faire du polling ?

4. Est-ce pertinent de séparer la partie acquisition d'image de la partie enregistrement (avec header fits) ?

5. Ok pour séparer la partie initialisation de la caméra (au démarrage de l'observatoire) de la partie acquisition ? 

6. A quoi sert la fonction Thumbnail ? Il me semble que je n'en ai pas besoin (et je peux simplifier... pas d'accès à numpy...)

7. OK pour faire un directory avec les devices INDI (bas niveau), et un autre avec les fns Haut Niveau (astro) ?

## A propos de PHD2

17/02/2024 - J'ai pas mal avancé ces derniers mois. Un peu avec Thibault, et un peu de mon côté;

Là, je veux gamberger un peu sur PHD2 ; j'ai pu le faire marcher, mais maintenant je veux fignoler la librairie qui me va bien.

Ce dont j'ai besoin :

- Fonctions de connexion, du serveur et du profil
- Fonctions de base (qui n'attendent pas que l'action soit terminée)
  - TakeImage
  - Loop
  - Findstar
  - startGuiding
  - StopGuiding
- Fonctions spectro
  - GuideFromTo
  - Gérer le cas de 'star lost'

## Organisation générale du logiciel

14/12/2024 - une nouvelle fois, je reprends le boulot de développement (après la dynamique des RCE).

J'ai pris quelques décisions structurelles (du type "il y a maintenant 5 modules indépendants"). Je me concentre ici sur le module "séquence d'observation" qui est le plus critique à l'heure actuelle. L'objectif est donc d’enchaîner une observation complète - considérant que les conditions sont bonnes et que l'observatoire est ouvert. 

J'ai maintenant 3 fichiers qui décrivent le contexte :

- Le fichier qui décrit l'observatoire (coordonnées, nom de l'observatoire, etc)
- Le fichier qui décrit les devices disponibles (INDI)
- Le fichier qui décrit la cible en cours d'observation

Je bute sur un problème d'organisation du logiciel.

J'ai des fonctions de bas niveau, qui ne concernent qu'un seul device (prendre une image, pointer le télescope). Par ailleurs, j'ai des fonctions de haut-niveau, qui réalisent une activité astronomique. Du genre "autofocus", ou "mettre l'étoile dans la fente". Ces fonctions travaillent (quasiment ?) toutes avec plusieurs devices (typiquement télescope + caméra). 

J'aimerais que chaque fonction, de bas niveau comme de haut niveau, puisse être appelée par une API Rest. Ca me semble important pour le debug. Le problème est de savoir comment je passe les paramètres (en gros les 3 fichiers ci-dessus) aux fonctions ; et là je pense surtout aux fonctions de haut niveau (mais ça concerne peut-être aussi les bas niveau).

En fonctionnement normal, c'est le séquenceur d'observation qui va lire les fichiers, puis passer les infos (3 fichiers) en paramètres. En procédant ainsi, je ne lis les fichiers qu'une seule fois, puis je les garde en mémoire pour toute l'observation. 

Mais si je veux passer par une API, ça ne va pas le faire, puisque je n'aurai pas en mémoire les fameux trois fichiers.

Faut-il alors que chaque opération lise les 3 fichiers ? Ca me semble carrément très lourd - et pas beau.

Peut-être une option : ne lire à chaque fois les 3 fichiers uniquement dans le cadre des API. Cela veut dire que je fais une première fonction qui lit les 3 fichiers, que j'appelle systématiquement dans les API, puis ensuite j'appelle chaque fonction astronomique. 

Cela ne marchera que si je n'ai pas besoin de passer d'autre paramètre que les 3 fichiers à chacune des fonctions, haut ou bas niveau. Je pense que c'est jouable - et ce sera même un des éléments fondamentaux de l'organisation du logiciel - mais c'est à vérifier. Cela implique aussi que chaque fonction ne retourne pas de valeur particulière, en dehors d'un statut (success / failed).

Je pense par ailleurs que je vais rapidement séparer les fonctions bas niveau et haut niveau dans des fichiers python séparés. Pour une meilleure lisibilité (le découpage est simple à décrire).