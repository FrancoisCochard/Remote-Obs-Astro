# Base SQL pour les cibles à observer

02/10/2022, St-Pancrasse

Je démarre la création d'une petite base de données SQLite pour héberger les objets à observer.

Je fais ça en mode "petits pas" - j'ai juste envie de pouvoir remplir cette base de données à partir de Simbad.

Pour ne pas m'enfermer dans cet outil (SQLite), je dois avoir une couche d'abstraction : quand je vais chercher des infos sur une étoile, je ne sais pas que c'est du SQLite derrière.

Je dois d'abord disposer d'un objet (classe) "Target", et cette classe doit avoir deux méthodes : une pour écrire dans la BDD, et l'autre pour lire.

... à suivre...