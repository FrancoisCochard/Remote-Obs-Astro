# Base SQL pour les cibles à observer

02/10/2022, St-Pancrasse

Je démarre la création d'une petite base de données SQLite pour héberger les objets à observer.

Je fais ça en mode "petits pas" - j'ai juste envie de pouvoir remplir cette base de données à partir de Simbad.

Pour ne pas m'enfermer dans cet outil (SQLite), je dois avoir une couche d'abstraction : quand je vais chercher des infos sur une étoile, je ne sais pas que c'est du SQLite derrière.

Je dois d'abord disposer d'un objet (classe) "Target", et cette classe doit avoir deux méthodes : une pour écrire dans la BDD, et l'autre pour lire.

09/12/2023 Je reprends ce petit script, pour aller vers une fonction en API Rest qui permet de récupérer les coordonnées d'une étoile (dans la perspective d'avoir un zcheduler en API Rest)

Je peux ouvrir la base de données avec "DB Browser for SQLite". Cela permet de voir et manipuler les données.

Je peux aussi lancer le script de gestion de la BD : 

- je commence par lance une console python (dans un terminal : python - après avoir été dans le bon répertoire... l'alias di fait le job).
- puis j'importe le script : from TargetDatabase.TargetBase import TargetBase as tb
- puis je déclare un objet "base de données" : A = tb()
- Puis le peux accéder aux commandes. Par exemple : F = A.query_List_TargetID() (puis print(F))

... à suivre...