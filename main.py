import requests
import pandas as pd
import user
import re
from bs4 import BeautifulSoup
# I think it works only on windows, adapt for linux
from winotify import Notification
import schedule
import time


def process_table(file_or_link):
    """
    Function to process the table in the html file.
    :param file_or_link: Either a file html or the response of a request (so a string).
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
                    descriptifs.append(cell.text)
                    matieres.append(matiere)
                if row.find_all("td", {"class": "bodyCC"}):
                    bodyCC_values = [td.text for td in row.find_all("td", {"class": "bodyCC"})]
                    if bodyCC_values:
                        bodyCC.append(bodyCC_values)

            for i in range(len(matieres)):
                data.append(
                    [matieres[i], descriptifs[i], bodyCC[i][0], bodyCC[i][1], bodyCC[i][2], bodyCC[i][3]])

                pattern = r"\n"
            for obj in data:
                for i in range(len(obj)):
                    obj[i] = re.sub(pattern, "", obj[i])
                # print(obj)

            df = pd.DataFrame(data, columns=["Matière", "Descriptif", "Date", "Moyenne", "Coef", "Note"])

            # Export in csv
            # df.to_csv("notes.csv", sep="\t", index=False)
            # print('-' * 100)
            # print(df)
            # print('-' * 100)
            return df
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
    file = open("resultRequest.html", "w", encoding="utf-8")
    file.write(result)
    file.close()


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
    TODO : Replace the credential by the generate_key() and get_info() function. But it doesn't work for the moment.
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
        export_to_html(reponse)

        # print("Reponse requete : " + r.text)
        # print("Reponse avec filtre : " + reponse)
        return reponse


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
    # TODO: Alors ca marche mais faut comprendre comment c'est fait
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
    old_note = process_table("resultRequest.html")
    look_for_new_note = process_table(request())

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
            new_note(to_print)

    else:
        print("Pas de nouvelles notes ou de différences détectées")
        new_note("Aucune nouvelle notes")
    # Enregistrez les nouvelles données dans le fichier CSV
    # new_data.to_csv("anciennes_notes.csv", sep="\t", index=False)


def new_note(message):
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


if __name__ == "__main__":
    schedule.every(1).minutes.do(is_new_note)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            print("Waiting...")

    except KeyboardInterrupt:
        exit(0)
