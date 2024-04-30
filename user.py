import keyring as kr
import getpass
#FIXME: La plus part des entêtes sont inutiles, il faudrait les supprimer
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
                  'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
}
headerPost = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
                  'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3 Referer: '
                       'https://gaps.heig-vd.ch/consultation/controlescontinus/consultation.php?idst=18672',
}

url = "https://gaps.heig-vd.ch/consultation/horaires/?annee=2023&trimestre=1&type=2&id=18672"
urlControleContinu = "https://gaps.heig-vd.ch/consultation/controlescontinus/consultation.php?idst=18672"

APP_NAME = "autogaps"

def save_credentials():
    # TODO check that no credentials exist, otherwise override
    print("Your AAI credentials will be stored in the system keyring.")
    username = input("Input your username (first.last): ")
    print("Hello : " + username)
    password = getpass.getpass("Enter your password: ")
    kr.set_password(APP_NAME, username, password)  # TODO add try/except


# Could use some error handling
def get_credentials():
    cred = kr.get_credential(APP_NAME, None)
    if cred is None:
        save_credentials()
        cred = kr.get_credential(APP_NAME, "")
    assert cred is not None
    return cred


MAIL = get_credentials().username
PASS = get_credentials().password
