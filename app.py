import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from PIL import Image
import os
import json

# 🔥 Firebase Admin SDK mit Umgebungsvariable initialisieren
firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials_json:
    raise ValueError("Fehlende Umgebungsvariable: FIREBASE_CREDENTIALS")

try:
    firebase_credentials = json.loads(firebase_credentials_json)
except json.JSONDecodeError:
    raise ValueError("Ungültiges JSON in der Umgebungsvariable FIREBASE_CREDENTIALS")

cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://textures-5c13e-default-rtdb.europe-west1.firebasedatabase.app/'
})

# Zugriff auf die Realtime Database
ref = db.reference('textures')

# Flask-App erstellen
app = Flask(__name__)

# Ordner für generierte Bilder
IMAGE_FOLDER = "static/textures"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Startseite mit Suchfunktion
@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    all_textures = ref.get() or {}

    # Suche nach Texturen
    filtered_textures = {key: value for key, value in all_textures.items() if search_query.lower() in key.lower()}
    
    return render_template('index.html', textures=filtered_textures, search_query=search_query)

# API zum Speichern einer neuen Textur
@app.route('/add_texture', methods=['POST'])
def add_texture():
    texture_id = request.form.get('texture_id', '').strip()
    colors_input = request.form.get('colors', '').strip()
    pattern_input = request.form.get('pattern', '').strip()

    if not texture_id or not colors_input or not pattern_input:
        return "Fehlende Daten", 400

    # Farben verarbeiten
    colors = {}
    for line in colors_input.split("\n"):
        if ":" in line:
            code, rgb = line.split(":")
            colors[code.strip()] = rgb.strip()

    # Muster verarbeiten
    pattern = [line.strip() for line in pattern_input.split("\n") if line.strip()]

    # In Firebase speichern
    ref.child(texture_id).set({"colors": colors, "pattern": pattern})

    return redirect(url_for('index'))

# API zum Generieren einer Textur
@app.route('/generate_texture/<texture_id>')
def generate_texture(texture_id):
    texture = ref.child(texture_id).get()
    if not texture:
        return f"Textur mit ID '{texture_id}' nicht gefunden.", 404

    colors = texture['colors']
    pattern = texture['pattern']
    
    # Erstelle ein Bild mit Transparenz (RGBA-Modus)
    img = Image.new("RGBA", (16, 16), color=(255, 255, 255, 0))  # Vollständig transparent

    for y, row in enumerate(pattern):
        for x, code in enumerate(row.split()):
            if code in colors:
                rgb = colors[code].split(',')
                if rgb == ["999", "999", "999"]:  
                    img.putpixel((x, y), (0, 0, 0, 0))  # Transparenter Pixel
                else:
                    rgba = tuple(map(int, rgb)) + (255,)  # Volle Deckkraft
                    img.putpixel((x, y), rgba)

    # Bild speichern im static-Ordner
    img_path = os.path.join(IMAGE_FOLDER, f"{texture_id}.png")
    img.save(img_path)

    return send_file(img_path, mimetype='image/png', as_attachment=True, download_name=f"{texture_id}.png")

# API zum Abrufen aller Texturen als JSON
@app.route('/get_textures', methods=['GET'])
def get_textures():
    textures = ref.get() or {}
    return jsonify(textures)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
