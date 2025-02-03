import firebase_admin
from firebase_admin import credentials, db
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk

# Firebase Admin SDK initialisieren
cred = credentials.Certificate('Hier Rein Dein Phad von firebase_credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://textures-5c13e-default-rtdb.europe-west1.firebasedatabase.app/'  # Deine Firebase-Datenbank-URL
})

# Zugriff auf die Realtime Database
ref = db.reference('textures')

# Funktion zum Abrufen aller Texturen aus Firebase
def get_all_textures_from_firebase(search_query=""):
    all_textures = ref.get()
    if all_textures:
        # Filtere die Texturen nach dem Suchbegriff
        filtered_textures = {key: value for key, value in all_textures.items() if search_query.lower() in key.lower()}
        return filtered_textures
    else:
        return {}

# Funktion zum Abrufen einer Textur aus Firebase
def get_texture_from_firebase(texture_id):
    texture_ref = ref.child(texture_id)
    texture = texture_ref.get()  # Abrufen der Textur-Daten
    if texture:
        return texture
    else:
        return None

# Funktion zum Hinzufügen einer Textur zu Firebase
def add_texture_to_firebase(texture_id, colors, pattern):
    texture_ref = ref.child(texture_id)
    texture_ref.set({
        'colors': colors,
        'pattern': pattern
    })
    messagebox.showinfo("Erfolg", f"Textur '{texture_id}' wurde zu Firebase hinzugefügt.")

# Funktion zum Erstellen eines Bildes aus einer Textur
def generate_texture_from_firebase(texture_id):
    texture = get_texture_from_firebase(texture_id)
    if texture:
        colors = texture['colors']
        pattern = texture['pattern']
        
        # Erstelle das Bild
        img = Image.new("RGB", (16, 16), color=(255, 255, 255))  # Weißer Hintergrund
        
        # Muster in das Bild übertragen
        for y, row in enumerate(pattern):
            for x, code in enumerate(row.split()):
                if code in colors:
                    rgb = tuple(map(int, colors[code].split(',')))
                    img.putpixel((x, y), rgb)
        
        # Wähle den Speicherort für das Bild
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG-Dateien", "*.png"), ("Alle Dateien", "*.*")])
        if save_path:
            # Bild speichern
            img.save(save_path)
            messagebox.showinfo("Erfolg", f"Textur gespeichert unter {save_path}")
    else:
        messagebox.showerror("Fehler", "Textur konnte nicht geladen werden.")

# Funktion zur Textur Erstellung mit beliebig vielen Farben und Muster im großen Textfeld
def create_texture():
    texture_id = simpledialog.askstring("Textur ID", "Gib eine ID für die Textur ein:")
    if texture_id is None:
        return
    
    # Farbcodes eingeben
    colors_input = simpledialog.askstring("Farben eingeben", "Gib die Farben als 'Code:RGB' ein (z.B. G1:168,224,106; G2:124,172,68):")
    if not colors_input:
        return
    
    # Farben aufteilen und als Dictionary speichern
    colors = {}
    color_entries = colors_input.split(";")
    for entry in color_entries:
        code, rgb = entry.split(":")
        colors[code.strip()] = rgb.strip()

    # Muster eingeben
    pattern_input = simpledialog.askstring("Muster eingeben", "Gib das Muster als 16 Zeilen mit je 16 Symbolen ein (z.B. 'G1 G2 G1 ...'):")
    if not pattern_input:
        return
    
    # Muster in Zeilen aufteilen
    pattern = pattern_input.split("\n")
    if len(pattern) != 16 or any(len(row.split()) != 16 for row in pattern):
        messagebox.showerror("Fehler", "Das Muster muss 16 Zeilen mit je 16 Werten enthalten.")
        return
    
    # Textur zu Firebase hinzufügen
    add_texture_to_firebase(texture_id, colors, pattern)

# Funktion zur Anzeige von hochgeladenen Texturen und Filtern
def show_textures():
    search_query = search_entry.get()
    textures = get_all_textures_from_firebase(search_query)

    # Lösche vorherige Texturen aus der Liste
    for item in texture_listbox.get_children():
        texture_listbox.delete(item)

    if textures:
        for texture_id in textures.keys():
            texture_listbox.insert("", "end", texture_id, values=(texture_id,))
    else:
        messagebox.showinfo("Keine Ergebnisse", "Keine Texturen gefunden.")

# Funktion zur Auswahl und Generierung einer Textur aus der Liste
def generate_selected_texture():
    selected_item = texture_listbox.selection()
    if selected_item:
        texture_id = texture_listbox.item(selected_item, "values")[0]
        generate_texture_from_firebase(texture_id)
    else:
        messagebox.showerror("Fehler", "Wähle zuerst eine Textur aus.")

# Funktion zum Beenden
def quit_app():
    root.quit()

# Erstelle das Hauptfenster
root = tk.Tk()
root.title("Textur Generator")

# Eingabefeld für die Suchanfrage
search_label = tk.Label(root, text="Suche nach Texturen:")
search_label.pack(pady=5)

search_entry = tk.Entry(root, width=40)
search_entry.pack(pady=5)

search_button = tk.Button(root, text="Suchen", command=show_textures)
search_button.pack(pady=5)

# Listbox zur Anzeige der Texturen
texture_listbox = ttk.Treeview(root, columns=("ID"), show="headings", height=10)
texture_listbox.heading("ID", text="Textur ID")
texture_listbox.pack(pady=10)

# Button zum Textur generieren
generate_button = tk.Button(root, text="Textur generieren", command=generate_selected_texture)
generate_button.pack(pady=10)

# Button zum Erstellen einer neuen Textur
create_button = tk.Button(root, text="Neue Textur erstellen", command=create_texture)
create_button.pack(pady=10)

# Button zum Beenden der Anwendung
quit_button = tk.Button(root, text="Beenden", command=quit_app)
quit_button.pack(pady=10)

# Starte das GUI
root.mainloop()
