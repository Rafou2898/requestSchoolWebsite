from cryptography.fernet import Fernet

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

MAIL = "add_Mail"
PASS = "add_Password"


def generate_key():
    # Générez une clé de chiffrement
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    # Chiffrez les informations d'identification
    username = MAIL.encode()
    password = PASS.encode()

    encrypted_username = cipher_suite.encrypt(username)
    encrypted_password = cipher_suite.encrypt(password)

    # Enregistrez les informations d'identification chiffrées dans un fichier
    with open('credentials.txt', 'wb') as file:
        file.write(encrypted_username)
        file.write(b'\n')  # Ajoute une ligne vide pour séparer les données
        file.write(encrypted_password)

    # Sauvegardez également la clé de chiffrement dans un endroit sûr
    with open('encryption_key.key', 'wb') as key_file:
        key_file.write(key)


# Probleme avec la decription du password
def get_info():
    # Chargez la clé de chiffrement à partir d'un endroit sûr
    with open('encryption_key.key', 'rb') as key_file:
        key = key_file.read()

    # Créez une instance de Fernet avec la clé
    cipher_suite = Fernet(key)

    # Lisez les informations d'identification chiffrées à partir du fichier
    with open('credentials.txt', 'rb') as file:
        encrypted_username = file.readline()
        file.readline()  # Ignore la ligne vide
        encrypted_password = file.readline()

    # Déchiffrez les informations d'identification
    username = cipher_suite.decrypt(encrypted_username).decode()
    print("username : ", username)
    password = cipher_suite.decrypt(encrypted_password).decode()
    return username, password
