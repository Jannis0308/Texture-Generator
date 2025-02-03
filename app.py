import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from PIL import Image
import os

# Firebase Admin SDK initialisieren
cred = credentials.Certificate('/workspaces/Texture-Generator/firebase_credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://textures-5c13e-default-rtdb.europe-west1.firebasedatabase.app/'  # Deine Firebase-Datenbank-URL
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
    search_query = request.args.get('search', '')
    all_textures = ref.get() or {}

    # Suche nach Texturen
    filtered_textures = {key: value for key, value in all_textures.items() if search_query.lower() in key.lower()}
    
    return render_template('index.html', textures=filtered_textures, search_query=search_query)

# API zum Speichern einer neuen Textur
@app.route('/add_texture', methods=['POST'])
def add_texture():
    texture_id = request.form['texture_id']
    colors_input = request.form['colors']
    pattern_input = request.form['pattern']

    # Farben verarbeiten
    colors = {}
    for line in colors_input.split("\n"):
        if ":" in line:
            code, rgb = line.split(":")
            colors[code.strip()] = rgb.strip()

    # Muster verarbeiten
    pattern = pattern_input.split("\n")

    # In Firebase speichern
    ref.child(texture_id).set({"colors": colors, "pattern": pattern})

    return redirect(url_for('index'))

# API zum Generieren einer Textur
@app.route('/generate_texture/<texture_id>')
def generate_texture(texture_id):
    texture = ref.child(texture_id).get()
    if not texture:
        return "Textur nicht gefunden", 404

    colors = texture['colors']
    pattern = texture['pattern']
    img = Image.new("RGB", (16, 16), color=(255, 255, 255))

    for y, row in enumerate(pattern):
        for x, code in enumerate(row.split()):
            if code in colors:
                rgb = tuple(map(int, colors[code].split(',')))
                img.putpixel((x, y), rgb)

    # Bild speichern
    img_path = os.path.join(IMAGE_FOLDER, f"{texture_id}.png")
    img.save(img_path)

    return send_file(img_path, mimetype='image/png', as_attachment=True, download_name=f"{texture_id}.png")

# API zum Abrufen aller Texturen als JSON
@app.route('/get_textures', methods=['GET'])
def get_textures():
    return jsonify(ref.get() or {})

if __name__ == '__main__':
    app.run(debug=True)
