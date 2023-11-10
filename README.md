# Projet Récupération de Notes sur GAPS

## Principe
Ce programme est principalement fait pour un étudiant à la heig. Il permet de récupérer les notes de l'étudiant
sur le site [Gaps](https://gaps.heig-vd.ch/) et de vérifier si une nouvelle note a été ajouter. Le but est de recevoir 
une notificatation dans le cas où il y a une nouvelle note. Pour l'instant, ce programme fonctionne uniquement sur windows.
Le but final est de pouvoir le faire fonctionne sur un téléphone android. Pourquoi pas sur d'autres systèmes, mais ce n'est pas 
la priorité. L'option qui est utilisée pour faire tourner le programme est pour l'instant un mix de l'option
[2.2](TODO.md/#option-22-executer-le-programme-en-tant-que-processus) et [5](TODO.md/#option-5-librairie-python-schedule).

**_Instruction :_** Pour utiliser le programme, il faut mettre ses identifiants gaps dans le fichier [user.py](user.py).

_Remarque :_ Il y a des fonctions de la librairie fernet qui dervrait permettre de chiffrer les identifiants, 
mais ça marche avec le mail, mais pas avec le mot de passe. Et pour le moment je ne sais pas pourquoi.

_Note :_ Le programme n'est pas encore fini, il y a des choses qui pourraient être changé ou amélioré.

