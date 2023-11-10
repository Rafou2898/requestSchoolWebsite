# Projet Récupération de Notes sur GAPS

## Principe
Ce programme est principalement fait pour un étudiant à la heig. Il permet de récupérer les notes de l'étudiant
sur le site [Gaps](https://gaps.heig-vd.ch/) et de vérifier si une nouvelle note a été ajouter. Le but est de recevoir 
une notificatation dans le cas où il y a une nouvelle note. Pour l'instant, ce programme fonctionne uniquement sur windows.
Le but final est de pouvoir le faire fonctionne sur un téléphone android. Pourquoi pas sur d'autres systèmes, mais ce n'est pas 
la priorité. L'option qui est utilisée pour faire tourner le programme est pour l'instant un mix de l'option
[2.2](#option-22-executer-le-programme-en-tant-que-processus) et [5](#option-5-librairie-python-schedule).

**_Instruction :_** Pour pouvoir lancer le programme, il faut mettre ses identifiants gaps dans le fichier [user.py](user.py).

_Remarque :_ Il y a des fonctions de la librairie fernet qui dervrait permettre de chiffrer les identifiants, 
mais ça marche avec le mail mais pas avec le mot de passe. Et pour le moment je ne sais pas pourquoi.

_Note :_ Le programme n'est pas encore fini, il y a des choses qui pourraient être changé ou amélioré.

## Code pour comparer les notes en csv et en BDR

#### Useful link

- [makeADockerImage](https://www.geeksforgeeks.org/how-to-run-a-python-script-using-docker/)
- [dockerForDataBase](https://commandprompt.com/education/how-to-install-postgresql-using-docker-compose/)

### CSV


```python
import pandas as pd

# Chargez les données précédemment enregistrées depuis le fichier CSV
old_data = pd.read_csv("anciennes_notes.csv", sep="\t")

# Effectuez une requête pour obtenir les nouvelles données
# ...

# Comparez les nouvelles données avec les anciennes données pour détecter les différences
new_data = pd.DataFrame(...)  # Remplacez ... par les nouvelles données obtenues
differences = new_data[~new_data.isin(old_data.to_dict(orient='list'))].dropna()

# Si des différences sont détectées, effectuez une action (par exemple, envoyer une notification)
if not differences.empty:
    print("Nouvelles notes détectées :")
    print(differences)

# Enregistrez les nouvelles données dans le fichier CSV
new_data.to_csv("anciennes_notes.csv", sep="\t", index=False)

```

### BDR

```python

import sqlite3
import pandas as pd

# Établissez une connexion à la base de données SQLite
conn = sqlite3.connect("notes.db")

# Créez une table pour stocker les notes si elle n'existe pas déjà
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        Matière TEXT,
        Descriptif TEXT,
        Date TEXT,
        Moyenne REAL,
        Coef TEXT,
        Note REAL
    )
""")
conn.commit()

# Effectuez une requête pour obtenir les nouvelles données
new_data = pd.DataFrame(...)  # Remplacez ... par les nouvelles données obtenues

# Comparez les nouvelles données avec les anciennes données dans la base de données
cursor.execute("SELECT * FROM notes")
old_data = pd.DataFrame(cursor.fetchall(), columns=["Matière", "Descriptif", "Date", "Moyenne", "Coef", "Note"])
differences = new_data[~new_data.isin(old_data.to_dict(orient='list'))].dropna()

# Si des différences sont détectées, effectuez une action (par exemple, envoyer une notification)
if not differences.empty:
    print("Nouvelles notes détectées :")
    print(differences)

# Enregistrez les nouvelles données dans la base de données
new_data.to_sql("notes", conn, if_exists="replace", index=False)

# Fermez la connexion à la base de données
conn.close()
    
```


## Idée pour envoyer les informations en arrière plan

### Option 1: Raspberry Pi

Si vous souhaitez exécuter votre programme en continu sur un Raspberry Pi, voici comment vous pouvez le faire :

Raspberry Pi : Assurez-vous que votre Raspberry Pi est configuré et opérationnel. Vous aurez besoin d'une connexion Internet et d'un système d'exploitation tel que Raspberry Pi OS.

Déploiement : Copiez votre programme Python sur le Raspberry Pi. Vous pouvez le faire en utilisant une clé USB, SCP, ou d'autres méthodes de transfert de fichiers.

Planification : Utilisez le planificateur de tâches intégré (Cron) de Linux pour exécuter votre programme à intervalles réguliers. Par exemple, pour exécuter votre script toutes les heures, ajoutez une ligne dans la table de cron :

code: 

`0 * * * * /usr/bin/python3 /chemin/vers/votre_script.py`

Assurez-vous d'adapter le chemin vers votre script Python.

Exécution : Le Raspberry Pi exécutera automatiquement votre programme à l'heure spécifiée dans la tâche Cron.

### Option 2: Exécution en arrière-plan sur Windows 10
#### Option 2.1: Planificateur de tâches de Windows

Si vous préférez exécuter le programme en arrière-plan sur Windows 10, suivez ces étapes :

Planification : Utilisez le Planificateur de tâches de Windows pour créer une tâche planifiée. Vous pouvez spécifier la fréquence d'exécution (par exemple, toutes les heures) et exécuter votre script Python en arrière-plan.

Paramètres de sécurité : Assurez-vous que le script a les bonnes autorisations pour s'exécuter. Vous pouvez spécifier l'utilisateur sous lequel la tâche planifiée s'exécute.

Exécution : Le Planificateur de tâches de Windows exécutera automatiquement votre script Python à l'heure spécifiée.

#### Option 2.2: Executer le programme en tant que processus

On peut lancer un porgramme en arrière plan avec `pythonw.exe main.py` (dans le repertoire ou est le fichier)-
Pour connaitre si le process est actif et savoir son PID on peut executer cette commande `Get-Process | where ProcessName -Match python`
et pour arreter le process on peut utiliser `Stop-Process -Id <PID>`

### Option 3: Containers (Docker)

Si vous préférez utiliser Docker pour exécuter votre programme en continu, suivez ces étapes :

Docker : Assurez-vous que Docker est installé sur votre ordinateur (que vous utilisez Windows 10).

Dockerfile : Créez un fichier Dockerfile qui spécifie comment votre application Python doit être mise en conteneur.

Construction de l'image : Utilisez la commande docker build pour construire une image Docker à partir de votre Dockerfile. Par exemple : docker build -t mon_app .

Exécution du conteneur : Utilisez la commande docker run pour exécuter votre conteneur. Assurez-vous de spécifier le bon port et de mapper les volumes si nécessaire.

code:

`docker run -it --rm --name my-running-script -v "C:\Users\rafae\Desktop\git_projects\requestSchoolWebsite:/usr/src/myapp" -w /usr/src/myapp python:3 sh -c "pip install -r requirements.txt && python main.py"
p`

Cela exécutera votre script Python dans un conteneur Docker.

### Option 4: Android (Java)

Pour exécuter un programme en Java sur Android, vous devrez créer une application Android. Voici comment vous pouvez faire :

Création d'une application Android : Vous devrez créer une application Android en utilisant Java et les outils de développement Android, tels qu'Android Studio.

Intégration du code : Ajoutez votre code Java dans le projet Android. Vous pouvez créer une tâche ou un service qui s'exécute en arrière-plan pour effectuer la vérification des notes et les notifications.

Programmation : Programmez votre application Android pour effectuer la vérification des notes à intervalles réguliers. Vous pouvez utiliser un service Android ou des alarmes pour déclencher cette vérification.

Notifications : Utilisez les fonctionnalités d'Android pour afficher des notifications lorsqu'il y a de nouvelles notes.

Déploiement : Déployez votre application Android sur un appareil Android ou un émulateur pour qu'elle fonctionne en continu.

### Option 5: Librairie python schedule

```python
import schedule
import time

# Fonction à exécuter
def mon_script():
# Votre code Python ici

# Planifier l'exécution toutes les 30 minutes
schedule.every(30).minutes.do(mon_script)

# Boucle pour maintenir le script en cours d'exécution
while True:
    schedule.run_pending()
    time.sleep(1)
```