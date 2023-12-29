# Analyse des états - machine d'états initiale

Avant de changer des choses, je commence par analyser comment fonctionne ce qui est proposé. A première vue, j'ai un peu du mal à comprendre la logique ; disons que je n'aurais pas fait comme ça.

Note : pour vérifier que j'ai la main sur les étapes, j'ai ajouté une étape "totoFC". Je ne la prends pas en compte ici.

Si je comprends bien la logique de la machine d'état, à chaque état est associée une méthode du même nom, qui est lancée "on_enter". Donc par exemple la lib "parked.py" est lancée quand on arrive dans l'état "parked". Sauf que... au débit de la méthode on_enter(), on trouve un message "entering parking state"

Je ne comprends pas bien la nuance entre le 'Model' et la 'Machine'. Ce que je vois, c'est que la machine contient le modèle, les étapes et les transitions. Ai-je raison de dire que la Machinbe est la classe (la "matrice"), et le modèle en est une instanciation ? 

Je constate que le "model" contient un "manager", qui semble gérer l'ensemble de l'observatoire. Bigre - pourquoi un manager au-dessus de la machine d'état, alors que la gestion de tout l'observatoire pourrait être géré par la machine d'état ??

Au passage, je note que le fichier simple_state_table.yaml est passé en argument (ou plutôt c'est la valeur par défaut), ce qui sous-entend qu'on pourrait passer en argument d'autres machines d'état... tiens, tiens... très inétressant !

Concernant les messages de log, je vois qu'il y en a de deux types : model.logger.debug(msg) et model.say(msg)... c'est quoi la nuance ?

### parked

Regarde si il y a (encore) des observations à faire (sinon, on réessaie dans 30 minutes).
Si il y en a, il passe en mode ready
Je vois que le "model" gère pas mal de flags (should_retry, is_safe, is_dark...)
Un truc qui me gratte, c'est que "parked" n'est pas un état de l'observatoire, ni du cycle d'observation, mais un état de la monture. Un peu confus tout ça.

### sleeping (état initial)

C'est l'état d'attente ? Un peu étonnant...

### housekeeping

Fait du ménage : model.manager.cleanup_observations()
J'magine que la fonction de cette étape consiste à clôturer d'éventuelles observation sincomplètes ?

### calib_acq

Là, j'ai du mal à comprendre. Le besoin de calibration est très dépendant des observations...
Quand l'étape est terminée, ça repart en "house keeping"

### ready

Encore une étape étonnante. On ne fait que vérifier que l'obs est dispo et le télescope déparqué... et ensuite on passe à scheduling.

### scheduling

On demande la prochaine observation au manager, et on vérifie que le champ visé est accessible (ce qui a déjà été fait par le manager)... de nouveau, j'ai l'impression que "scheduling n'est pas une étape de la machine d'état..."

### slewing

Là, c'est clair : le télescope pointe. Là où je trouve ça étonnant, c'est la nuance avec Pointing...

### pointing

Bon... en fait, c'est assez clair : il s'agit là de l'étape de plate solving. ok, je comprends la nuance. Mais attention : en spectro, le plate solving ne marche pas systématiquement - parce qu'on a potentiellement peu d'étoiles dans le champ.

### tracking

Je n'arrive pas à voir si il s'agit d'activer le tracking (sur ma monture, il l'est par défaut...), pou si c'est l'activation de l'autoguidage. Le code de cette librairie ne mentionne pas d'autoguidage. Pourtant, ça me parait une étape importante en spectro - mais je ne sais pas si c'est de nouveau une étape. Je ne crois pas en fait.

### focusing

Ok, la fonction est simple est claire. Ce qui m'étonne, c'est de le faire APRES le plate solving. Je l'aurais fait avant, pour détecter plus d'étoiles dans le champ.

### observing

La fonction est facile à comprendre. Par contre, la méthode est encore étonnante :c'est fait de nouveau par un appel au manager. C'est vraiment central ce machin !

### analyzing

Je suppose que ça lance la réduction de données. Pour le moins, le terme "analyzing" me semble mal choisi.

### parking

Parque la monture et ferme l'observatoire (le deux font appel à model.manager)