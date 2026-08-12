import os
import io
from pathlib import Path
from flask import Flask, request, render_template_string, send_file, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

TEST_LOGIN = os.getenv("TEST_LOGIN", "testuser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testpass")

# Icônes factices en base64
ICON_IMPRIMER = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5QERDQsZx8jvFQAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAvSURBVDjLY2AYBaNgFIyCgQNcQfn/R0Ac8Q9EMf6HqkHEQbgLQokLQ+IFQVFCaBhQAAAiFgX+4xLq2gAAAABJRU5ErkJggg=="
ICON_TELECHARGER = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5QERDQsZx8jvFQAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAxSURBVDjLY2AYBaNgFIyCgQNcQfn/0dAQhxBkRCEeBlDEGHCpBCoOQQAhKAQHQAAABJVgA+ubxEoAAAAASUVORK5CYII="

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>eCar WebEDI</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:Arial,Helvetica,sans-serif; }
body { height:100vh; background:linear-gradient(to right,#b7d5ef,#d8e8f6); display:flex; justify-content:center; align-items:center; }
.logo { text-align:center; margin-bottom:35px; }
.logo h1 { color:white; font-size:55px; font-weight:bold; }
.login-box { width:540px; }
.card { background:white; border-radius:18px; overflow:hidden; box-shadow:0 8px 25px rgba(0,0,0,.18); }
.card-header { background:#0d6fb8; height:70px; position:relative; }
.avatar { position:absolute; right:25px; top:-22px; width:60px; height:60px; border-radius:50%; background:white; display:flex; justify-content:center; align-items:center; font-size:28px; }
.content { padding:40px; }
.content h2 { color:#555; margin-bottom:30px; font-weight:normal; }
.row { display:flex; margin-bottom:25px; align-items:center; }
.row label { width:150px; color:#666; }
.row input { flex:1; border:none; border-bottom:1px solid #CCC; padding:8px; outline:none; }
button { width:100%; background:#2b95e6; color:white; border:none; padding:12px; border-radius:4px; cursor:pointer; font-size:15px; }
button:hover { background:#1f82cf; }
.forgot { text-align:center; margin-top:15px; }
.forgot a { text-decoration:none; color:#5c7ca0; }
.error { color:red; margin-top:15px; }
.flag { position:absolute; top:20px; right:20px; font-size:25px; }
</style>
</head>
<body>
<div class="flag">🇫🇷</div>
<div class="login-box">
<div class="logo"><h1>eCar</h1><div style="color:white;font-size:32px;">WebEDI</div></div>
<div class="card">
<div class="card-header"><div class="avatar">👤</div></div>
<div class="content">
<h2>Veuillez vous identifier</h2>
<form method="POST">
<div class="row"><label>Utilisateur</label><input type="text" name="A19"></div>
<div class="row"><label>Mot de passe</label><input type="password" name="A25"></div>
<button id="A784">CONNEXION</button>
</form>
<div class="forgot"><a href="#">Mot de passe oublié ?</a></div>
{% if error %}<p class="error">{{error}}</p>{% endif %}
</div>
</div>
</div>
</body>
</html>
"""

MESSAGES_TABLE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>eCar WebEDI</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:Arial,Helvetica,sans-serif; }
body { background:#edf2f7; }
.wrapper { display:flex; min-height:100vh; }
.sidebar { width:260px; background:#0f67ad; color:white; }
.logo { height:88px; display:flex; justify-content:center; align-items:center; font-size:36px; font-weight:bold; border-bottom:1px solid rgba(255,255,255,.15); }
.user { padding:22px; font-size:18px; border-bottom:1px solid rgba(255,255,255,.15); }
.menu a { display:block; padding:18px 28px; color:white; text-decoration:none; font-size:18px; }
.menu a:hover { background:#0a568f; }
.main { flex:1; }
.topbar { height:88px; background:white; display:flex; justify-content:space-between; align-items:center; padding:0 35px; box-shadow:0 2px 8px rgba(0,0,0,.08); }
.title { font-size:50px; color:#555; font-weight:300; }
.icons { font-size:28px; }
.content { padding:25px; }
.filters { background:white; padding:18px; margin-bottom:18px; display:flex; gap:15px; align-items:flex-end; box-shadow:0 2px 8px rgba(0,0,0,.08); }
.filter { display:flex; flex-direction:column; }
.filter label { font-size:13px; color:#666; margin-bottom:6px; }
.filter input, .filter select { width:180px; padding:8px; border:1px solid #ccc; border-radius:3px; }
table { width:100%; border-collapse:collapse; background:white; box-shadow:0 2px 8px rgba(0,0,0,.08); }
thead { background:#2b98e5; color:white; }
th { padding:16px; text-align:left; font-weight:normal; }
td { padding:14px; border-bottom:1px solid #eee; }
tbody tr:hover { background:#f7fbff; }
.status { color:#3f82d7; }
.actions { white-space:nowrap; }
.actions a { margin-right:8px; }
.actions img { width:22px; height:22px; vertical-align:middle; }
</style>
</head>
<body>
<div class="wrapper">
<div class="sidebar">
<div class="logo">eCar</div>
<div class="user">👤 COFAT1_SIT</div>
<div class="menu">
<a href="#">🏠 ACCUEIL</a>
<a href="#">📄 RÉCAPITULATIF</a>
<a href="#">⚙ ADMINISTRATION</a>
</div>
</div>
<div class="main">
<div class="topbar">
<div class="title">Récapitulatif des messages</div>
<div class="icons">🇫🇷 ❓ ⏻</div>
</div>
<div class="content">
<div class="filters">
<div class="filter"><label>Partenaire</label><select><option>-- tous --</option></select></div>
<div class="filter"><label>Messages</label><select><option>-- tous --</option></select></div>
<div class="filter"><label>Du</label><input type="date"></div>
<div class="filter"><label>Au</label><input type="date"></div>
</div>
<table>
<thead>
<tr>
<th>Partenaire</th><th>Type</th><th>N° message</th><th>Statut</th><th>Date</th><th style="width:110px;">Actions</th>
</tr>
</thead>
<tbody>
{% for msg in messages %}
<tr>
<td>{{msg.partenaire}}</td>
<td>{{msg.type}}</td>
<td>{{msg.numero}}</td>
<td class="status">{{msg.statut}}</td>
<td>{{msg.date}}</td>
<td class="actions">
{% if msg.type=="Avis d'expédition" or msg.type=="Programme de Livraison Prévisionnel" or msg.type=="Appel de livraison" %}
<a href="/imprimer/{{msg.id}}"><img src='""" + ICON_IMPRIMER + """' alt=""></a>
<a href="/download/{{msg.id}}"><img src='""" + ICON_TELECHARGER + """' alt=""></a>
{% endif %}
</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
</div>
</div>
</body>
</html>
"""

# Base de données factice
messages_db = [
    # {"id": 4, "partenaire": "Fournisseur D", "type": "Avis d'expédition", "numero": "MSG-004", "statut": "Envoyé", "date": "Mer 17/07/2026 (10:00)"},
    {"id": 1, "partenaire": "Fournisseur E", "type": "Avis d'expédition", "numero": "MSG-005", "statut": "Envoyé", "date": "Mer 17/07/2026 (11:00)"},
    {"id": 3, "partenaire": "Fournisseur F", "type": "Avis d'expédition", "numero": "MSG-006", "statut": "Envoyé", "date": "Jeu 17/07/2026 (12:00)"},
    # {"id": 7, "partenaire": "Fournisseur K", "type": "Avis d'expédition", "numero": "MSG-007", "statut": "Envoyé", "date": "Jeu 16/07/2026 (12:00)"},
    # {"id": 8, "partenaire": "Fournisseur Y", "type": "Avis d'expédition", "numero": "MSG-008", "statut": "Envoyé", "date": "Jeu 16/07/2026 (12:00)"},
    # {"id": 9, "partenaire": "Fournisseur W", "type": "Avis d'expédition", "numero": "MSG-009", "statut": "Envoyé", "date": "Jeu 16/07/2026 (12:00)"},
    # {"id": 10, "partenaire": "Fournisseur W", "type": "Avis d'expédition", "numero": "MSG-0010", "statut": "Envoyé", "date": "Jeu 16/07/2026 (12:00)"},
    # {"id": 11, "partenaire": "Fournisseur 10", "type": "Avis d'expédition", "numero": "MSG-0011", "statut": "Envoyé", "date": "Jeu 16/07/2026 (12:00)"},
    # {"id": 12, "partenaire": "Fournisseur 10", "type": "Avis d'expédition", "numero": "MSG-0012", "statut": "Envoyé", "date": "Jeu 16/07/2026 (12:00)"},
    # {"id": 13, "partenaire": "Fournisseur 10", "type": "Avis d'expédition", "numero": "MSG-0013", "statut": "Envoyé", "date": "Jeu 14/07/2026 (12:00)"},
    # {"id": 14, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0014", "statut": "Envoyé", "date": "Jeu 17/07/2026 (12:00)"},
    # {"id": 15, "partenaire": "Fournisseur 10", "type": "Appel de livraison", "numero": "MSG-0015", "statut": "Envoyé", "date": "Jeu 17/07/2026 (12:00)"},
    # {"id": 16, "partenaire": "Fournisseur 10", "type": "Appel de livraison", "numero": "MSG-0016", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 17, "partenaire": "Fournisseur 10", "type": "Appel de livraison", "numero": "MSG-0017", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 18, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0018", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 19, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0019", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 20, "partenaire": "Fournisseur D", "type": "Avis d'expédition", "numero": "MSG-0020", "statut": "Envoyé", "date": "Mer 17/07/2026 (10:00)"},
    # {"id": 21, "partenaire": "Fournisseur D", "type": "Avis d'expédition", "numero": "MSG-0021", "statut": "Envoyé", "date": "Mer 15/07/2026 (10:00)"},



    # {"id": 22, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0022", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 23, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0023", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 24, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0024", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 25, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0025", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 26, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0026", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 27, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0027", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 28, "partenaire": "Fournisseur 10", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0028", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},


    # {"id": 29, "partenaire": "Fournisseur 10", "type": "Appel de livraison", "numero": "MSG-0029", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 30, "partenaire": "Fournisseur 10", "type": "Appel de livraison", "numero": "MSG-0030", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 31, "partenaire": "Fournisseur 10", "type": "Appel de livraison", "numero": "MSG-0031", "statut": "Envoyé", "date": "Jeu 15/07/2026 (12:00)"},
    # {"id": 32, "partenaire": "Fournisseur D", "type": "Avis d'expédition", "numero": "MSG-0032", "statut": "Envoyé", "date": "Mer 17/07/2026 (10:00)"},







    # {"id": 33, "partenaire": "Fournisseur D", "type": "Avis d'expédition", "numero": "MSG-0033", "statut": "Envoyé", "date": "Mer 19/07/2026 (10:00)"},
    # {"id": 34, "partenaire": "Fournisseur F", "type": "Programme de Livraison Prévisionnel", "numero": "MSG-0034", "statut": "Envoyé", "date": "Jeu 19/07/2026 (12:00)"},
    # {"id": 35, "partenaire": "Fournisseur F", "type": "Appel de livraison", "numero": "MSG-0035", "statut": "Envoyé", "date": "Jeu 19/07/2026 (12:00)"},





]   

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("A19") == TEST_LOGIN and request.form.get("A25") == TEST_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("messages"))
        return render_template_string(LOGIN_PAGE, error="Identifiants incorrects")
    return render_template_string(LOGIN_PAGE, error=None)

@app.route("/messages")
def messages():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template_string(MESSAGES_TABLE, messages=messages_db)

@app.route("/download/<int:msg_id>")
def download_pdf(msg_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    pdf_files = {
        1:  "BL_000391.pdf",
        3:  "BL_000394.pdf",
        4:  "BL_000391_removed.pdf",
        7:  "BL_000401.pdf",
        8:  "BL_000402.pdf",
        9:  "BL_000403.pdf",
        10: "BL_000400.pdf",
        11: "BL_000405.pdf",
        12: "BL_000404.pdf",
        13: "BL_000394.pdf",
        14: "delinsME26072302560322.csv",
        15: "Appel_de_Livraison.pdf",
        16: "Appel_de_Livraison2.pdf",
        17: "Appel_de_Livraison3.pdf",
        18: "delinsME26051302470338.csv",
        19:"delinsME26052702100325.csv",
        20:"BL_000391 - Copie (2).pdf",
        21:"BL_000391 - Copie.pdf",


        28:"delinsME26051302470338 - Copie (2).csv",
        22:"delinsME26051302470338 - Copie (3).csv",
        23:"delinsME26051302470338 - Copie.csv",
        24:"delinsME26070902200319 - Copie (2).csv",
        25:"delinsME26070902200319 - Copie.csv",
        26:"delinsME26072302560322 - Copie (2).csv",
        27:"delinsME26072302560322 - Copie.csv",



        29:"Appel_de_Livraison - Copie.pdf",
        30:"Appel_de_Livraison2 - Copie.pdf",
        31:"Appel_de_Livraison3 - Copie.pdf",
        32:"BL_000391_removed - Copie.pdf",

        # 33:"",
        34:"delinsME26081204120326.csv",
        # 35:"",
    }

    if msg_id in pdf_files:
        file_name = pdf_files[msg_id]
        file_path = os.path.join(app.root_path, "data", file_name)
        if not os.path.exists(file_path):
            return f"Fichier {file_name} introuvable sur le serveur.", 404

        ext = Path(file_name).suffix.lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        mime = mime_map.get(ext, 'application/octet-stream')

        return send_file(
            file_path,
            mimetype=mime,
            as_attachment=True,
            download_name=file_name
        )

    # PDF factice
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    return send_file(io.BytesIO(pdf_content), mimetype="application/pdf",
                     as_attachment=True, download_name=f"message_{msg_id}.pdf")

@app.route("/imprimer/<int:msg_id>")
def imprimer_pdf(msg_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return f"<h3>Impression du message {msg_id} simulée</h3>"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)