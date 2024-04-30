import requests
import pandas as pd
import user
import re
from bs4 import BeautifulSoup
# I think it works only on windows, adapt for linux
from winotify import Notification
import schedule
import time
from colorama import Fore
import os
from html import unescape
from datetime import datetime

import psycopg2


# Used for a database connection but useless for now
hostname = ''
port = ''
username = ''
password = ''
database = ''

result_html = "files/resultRequest.html"
result_csv = "files/notes.csv"


def process_table(file_or_link, dbOrCsv):
    """
    Function to process the table in the html file.
    :param file_or_link: Either a file html or the response of a request (so a string).
    :param dbOrCsv: True if we want to export the result in a csv file, False if we want to export it to the database.
    :return: The table in a DataFrame.
    """

    is_request = False if has_html_extension(file_or_link) else True

    if is_request:
        soup = BeautifulSoup(file_or_link, "html.parser")

    else:
        with open(file_or_link, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

    result_div = soup.find("div", {"id": "result"})

    if result_div:
        table = result_div.find("table", {"class": "displayArray"})
        if table:
            matieres = []
            descriptifs = []
            data = []
            bodyCC = []
            matiere = ""

            for row in table.find_all("tr"):
                header_cell = row.find("td", {"class": "bigheader"})
                if header_cell:
                    matiere = header_cell.text.split(" - ")[0]
                cell = row.find("div", {"class": "formulaire_contenu_label"})
                if cell:
                    # TODO: J'essaie de faire en sorte que les caractères spéciaux soient affichés correctement mais ca marche pas...
                    specialCase = row.find("div", {"onclick": "toggleLMNodes(this.childNodes);"})

                    if specialCase:
                        # print("in special case")
                        # print(specialCase.text)
                        elements = row.find_all(id=True)
                        for element in elements:
                            id_attribute_value = element.get('id')
                            if 'long' in id_attribute_value:
                                descriptifs.append(element.text)
                    else:

                        descriptifs.append(cell.text)

                    matieres.append(matiere)
                if row.find_all("td", {"class": "bodyCC"}):
                    bodyCC_values = [td.text for td in row.find_all("td", {"class": "bodyCC"})]
                    if bodyCC_values:
                        bodyCC.append(bodyCC_values)

            for i in range(len(matieres)):
                data.append(
                    [matieres[i], descriptifs[i], bodyCC[i][0], bodyCC[i][1], bodyCC[i][2], bodyCC[i][3]])

                pattern = r"\\n"
                # FIXME: VOIR si des que ca marche je peux supprimer cette loop
                patternEsc = r"\\u00e9"
            for obj in data:
                for i in range(len(obj)):
                      obj[i] = re.sub(pattern, "", obj[i])
                      obj[i] = re.sub(patternEsc, "é", obj[i])
                # print(obj)
            if dbOrCsv:
                df = pd.DataFrame(data, columns=["Matière", "Descriptif", "Date", "Moyenne", "Coef", "Note"])

                df.to_csv(result_csv, sep="\t", index=False, encoding='utf-8')

                return df
            else:

                for obj in data:
                    for i in range(len(obj)):
                        if obj[i] == "-":
                            obj[i] = None
                        elif isinstance(obj[i], str):
                            try:
                                parsed_date = datetime.strptime(obj[i], '%d.%m.%Y')
                                obj[i] = parsed_date.strftime('%Y-%m-%d')
                            except ValueError:

                                continue
                print(data)
                return data
        else:
            print("Table non trouvée dans la balise 'result'")

            return None

    else:
        print("Balise 'result' non trouvée")
        return None


def export_to_html(result):
    """
    Allows the export of the result of the request in a html file.
    :param result: The result of the request.
    :return: None.
    """
    file = open(result_html, "w", encoding="utf-8")
    file.write(result)
    file.close()

#FIXME: Je peux supprimer ce filtrage je pense et voir si y a la même dnas l'app java
def filtre_response(text):
    """
    Function to filter the response of the request, words specific to the response of the Gaps request.
    :param text: The "html" string to filter.
    :return: The "html" string to filtered.
    """
    pattern = r"\+:(.+)@<"
    pattern2 = r">@\\(.+)\""
    pattern3 = r"\\\""
    pattern4 = r"\\\/"
    text = re.sub(pattern, "<", text)
    text = re.sub(pattern2, ">", text)
    text = re.sub(pattern3, "\"", text)
    text = re.sub(pattern4, "/", text)
    return text


def request():
    """
    Request to the Gaps website. In order to use it correctly is necessary write the credentials in the user.py file.
    :return: The response of the request.
    """

    with requests.session() as s:
        """
        credentials = user.get_info()
        MAIL, PASS = credentials
        """
        login_data = {"login": user.MAIL, "password": user.PASS, "submit": "enter"}
        note_request_data = {"rs": "smartReplacePart", "rsargs": "[\"result\",\"result\",null,null,null,null]"}

        s.post(user.url, data=login_data, headers=user.header)
        r = s.post(user.urlControleContinu,
                   data=note_request_data, headers=user.headerPost)

        reponse = filtre_response(r.text)


        print("reponse requete : " + r.text)
        print("typeOf  r.text : " , type(r.text))
        #FIXME: Aucune de ces methodes ne marche pour enlever les \n, je ne sais pas quel est le problème
        #Donc pour le moment je garde le filtre

        # reponse = r.content.decode("unicode-escape").replace("\\", "")
        # print("typeOf  reponse decode : " , type(r.text))
        # print("reponse decode : " + reponse)
        # new_reponse = reponse.strip()
        #reponse = r.text.replace("\n", "")
        #reponse = reponse.replace(r"\\n", "")
        #pattern = r"\\n"
        #reponse = re.sub(pattern, "", r.text)


        # On check si la réponse contient le message d'erreur de session expirée
        if not r.text.__contains__("Votre session a expiré"):
            export_to_html(reponse)

            return reponse
        else:
            return None


def has_html_extension(file):
    """
    Check whether the file has a html extension.
    :param file: The file to check.
    :return: True if the file has a html extension, False otherwise.
    """
    if file.endswith(".html"):
        return True
    else:
        return False


def compare_notes(old_data, new_data):
    """
    Compare the notes of the two DataFrames. Function not really useful.
    :param old_data: The old DataFrame.
    :param new_data: Thr new DataFrame.
    :return: A tuple with the differences and the changed values if they are any.
    """
    # Comparer les différences entre les deux DataFrames
    differences = new_data.merge(old_data, indicator=True, how='outer').loc[lambda x: x['_merge'] == 'right_only']

    # Comparer les valeurs différentes entre les deux DataFrames
    changed_values = pd.concat([new_data, old_data]).drop_duplicates(keep=False)

    return differences, changed_values


def is_new_note():
    """
    Main function of the program. It compares the old notes with the new ones by processing the tables and call the
    notification alert if there are new notes or differences.
    :return: None.
    """
    try:
        old_note = process_table(result_html, True )
        look_for_new_note = process_table(request(), True)
    except AttributeError:
        print(Fore.RED + "Une erreur est apparue dans la requête, vérifiez vos identifiants" + Fore.RESET)
        return exit(0)

    differences, changed_values = compare_notes(old_note, look_for_new_note)

    if not differences.empty or not changed_values.empty:
        print("Nouvelles notes ou différences détectées :")
        if not differences.empty:
            print("Nouvelles notes détectées :")
            print(differences)
        if not changed_values.empty:
            to_print = changed_values.drop(columns=["Coef", "Date", "Moyenne"]).to_string(index=False, header=False)
            print("Différences détectées :")
            print(to_print)
            notification(to_print)

    else:
        print("Pas de nouvelles notes ou de différences détectées")
        # new_note("Aucune nouvelle notes")


def notification(message):
    """
    Function to call the notification alert. Works only on windows.
    :param message: The message to display.
    :return: None.
    """

    toast = Notification(app_id="Notification de notes",
                         title="Ajout de notes",
                         msg=message,
                         duration="short")
    toast.show()


def first_time():
    """
    Function that is called the first time using this programm. It processes the request and create the html and csv files.
    """
    process_table(request(), True)


def insert_into_db():
    # process_table(request())
    conn = None
    try:
        conn = psycopg2.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            dbname=database,

        )

        # Créez un nouveau curseur
        cur = conn.cursor()

        # Exécutez une requête
        cur.execute('set search_path = notes;')
        cur.execute('SELECT * FROM noteongaps;')
        # cur.executemany('INSERT INTO noteongaps VALUES (%s, %s, %s, %s, %s, %s);', process_table(request(), False))
        # cur.execute("commit;")
        # cur.execute('SELECT * FROM noteongaps;')

        # Récupérez les résultats
        rows = cur.fetchall()
        for row in rows:
            print(row)

        # Fermez le curseur et la connexion
        cur.close()

    except Exception as e:
        print(f"Une erreur est survenue: {e}")
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    if not os.path.exists(result_html):
        first_time()

    # Do the request at the start of the program
    notification("Démarrage du programme")
    is_new_note()
    # Do the request every minute
    schedule.every(1).minutes.do(is_new_note)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        exit(0)
