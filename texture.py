import json
import firebase_admin
from firebase_admin import credentials, db

# Firebase Admin SDK initialisieren
cred = credentials.Certificate('/workspaces/Texture-Generator/firebase_credentials.json')  # Hier den Pfad zu deiner Firebase-JSON-Datei einfügen
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://textures-5c13e-default-rtdb.europe-west1.firebasedatabase.app/'  # Ersetze mit deiner Firebase-Datenbank-URL
})

# Zugriff auf die Realtime Database
ref = db.reference('textures')

# JSON-Datei einlesen
with open('textures.json', 'r') as file:
    textures = json.load(file)

# Texturen in Firebase hochladen
for texture_id, texture_data in textures.items():
    ref.child(texture_id).set(texture_data)
    print(f"Textur {texture_id} wurde hochgeladen.")

print("Alle Texturen wurden erfolgreich hochgeladen.")
