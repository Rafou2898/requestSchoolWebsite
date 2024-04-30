# Projet Récupération de Notes sur GAPS
## Principe

Ce programme est principalement conçu pour un étudiant à la HEIG. Il permet de récupérer les notes de l'étudiant sur le site [Gaps](https://gaps.heig-vd.ch/) et de vérifier si une nouvelle note a été ajoutée. Le but est de recevoir une notification dans le cas où il y a une nouvelle note. Pour l'instant, ce programme fonctionne uniquement sur Windows.
Le but final est de pouvoir le faire fonctionner sur un téléphone Android. Pourquoi pas sur d'autres systèmes, mais ce n'est pas la priorité. 

**_Instruction :_** Pour lancer l'application, il faut exécuter `python main.py` dans une console. La première fois, il faut entrer ses identifiants pour accéder au site. Les bibliothèques Keyring et getpass vont permettre d'entrer les mots de passe une fois et de les enregistrer dans des services de verrouillage des ([Keyring Library](https://pypi.org/project/keyring/)). Dès que c'est enregistré, le programme devrait s'y connecter automatiquement au lancement du programme les fois suivantes.

Afin de télécharger toutes les librairies nécessaires, il faut exécuter la commande `pip install -r requirements.txt` dans le terminal.
Pour le moment, le programme envoie aussi une notification quand il n'y a pas de nouvelle note et chaque minute. Pour enlever cette notification, il faut supprimer la ligne  ` new_note("Aucune nouvelle notes")` dans la fonction `is_new_note()`.

_Note :_  Le programme n'est pas encore fini, il y a des choses qui doivent être changées ou améliorées et des fonctionnalités ajoutées.

