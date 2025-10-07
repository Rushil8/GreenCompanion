from flask import Flask,render_template,request,redirect,url_for,jsonify
import os
import requests
import json 
if not os.path.exists('user_garden.json'):
    with open('user_garden.json', 'w') as f:
        json.dump([],f)
from soil_classifier import classify_soil
from data_loader import load_soil_plants
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import json

import gdown
import os


def download_from_gdrive(file_id, dest_path):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    session = requests.Session()
    response = session.get(url, stream=True)
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(url, params=params, stream=True)
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

file_id = "10a-PPzKx6QwNFTBxKiMl5_axE_h7UhGU"
MODEL_PATH = "soil_model.h5"
download_from_gdrive(file_id, MODEL_PATH)
print("Model downloaded and saved.")

model = load_model(MODEL_PATH)

with open("class_indices.json") as f:
    class_indices = json.load(f)
    class_labels = {v: k for k, v in class_indices.items()}

def predict_soil_type(img_path):
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    confidence = float(np.max(prediction)) * 100
    return class_labels[predicted_class], confidence


def get_user_city():
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json
        city = data.get('city','Unknown')
        return city
    except Exception as e:
        print("Error getting city: {e}")
        return None

import firebase_admin
from firebase_admin import credentials, auth
from google.cloud import firestore

from flask import request, jsonify,session, redirect, render_template

app.secret_key = "supersecretkey"
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.Client.from_service_account_json("firebase_key.json")


@app.route("/verify-token",methods=["POST"])
def verify_token():
    id_token = request.json.get("idtoken")
    try:
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]
        return {"status": "success", "uid": user_id}
    except Exception as e:
        return {"status": "error", "message": str(e)},401

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            user = auth.get_user_by_email(email)
            session["user_id"] = user.uid
            return redirect("/dashboard")

        except Exception as e:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

@app.route("/sessionLogin",methods=["POST"])
def session_login():
    data = request.get_json()
    id_token = data.get("idToken")
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]

        session["user_id"] = uid
        return jsonify({"status": "success","uid":uid})
    except Exception as e:
        return jsonify({"status":"error","message": str(e)}), 401

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    
    weather_data = None
    if request.method == "POST":
        city = request.form.get("city")
        weather_data = get_weather(city)

    return render_template("dashboard.html", weather=weather_data)

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            return redirect("/login")
        except Exception as e:
            return render_template("register.html", error=str(e))

    return render_template("register.html")

@app.route("/logout",methods=["GET","POST"])
def logout():
    session.clear()
    return redirect("/login")

@app.route("/",methods=['GET','POST'])
def home():
    if "user_id" not in session:
        return redirect("/login")
    
    return redirect("/dashboard")
@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        file = request.files['soilimage']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
        
            predicted_soil, confidence = predict_soil_type(filepath)
            plants = load_soil_plants(predicted_soil)

            return render_template('result.html',soil_type = predicted_soil.capitalize(),confidence=round(confidence,2),plants=plants,image_url=filepath)
    return render_template('upload.html')

import json

@app.route('/save-garden', methods=['POST'])
def save_garden():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    selected_plants = request.form.getlist('plant')

    if not selected_plants:
        return "No plants selected"
    
    for plant in selected_plants:
        parts = plant.split("|")
        name = parts[0].strip()
        tip = parts[1].strip() if len(parts) > 1 else "Default care tip"
        season = parts[2].strip() if len(parts) > 2 else "Unknown"

        db.collection("users").document(user_id).collection("garden").document(plant).set({
            "name": name,
            "tip": tip,
            "season": season,
            "addedAt": firestore.SERVER_TIMESTAMP
        })
    
    garden_ref = db.collection("users").document(user_id).collection("garden").stream()
    garden = [doc.to_dict() for doc in garden_ref]
    return render_template('garden_saved.html', plants=garden)
    
@app.route('/my-garden')
def my_garden():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    garden_ref = db.collection("users").document(user_id).collection("garden").stream()
    garden = [doc.to_dict() for doc in garden_ref]
    
    return render_template('my_garden.html', plants=garden)


@app.route('/track', methods=['GET','POST'])
def track_growth():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    if request.method == 'POST':
        plant = request.form['plant']
        note = request.form['note']
        date = request.form['date']

        #entry = {"plant":plant, "note":note, "date":date,"createdAt": firestore.SERVER_TIMESTAMP}

        advice = []
        plant_doc = db.collection("users").document(user_id).collection("garden").document(plant).get()
        if plant_doc.exists:
            plant_info = plant_doc.to_dict()

            advice.append(plant_info.get("tip","-"))

            season = plant_info.get("season","").lower()
            if season == "summer":
                advice.append("Water daily in the early morning or evening.")
            elif season == "winter":
                advice.append("Water less frequently; protect from frost.")
            elif season == "rainy":
                advice.append("Ensure good drainage to avoid root rot.")
            
            advice.append("Check for pests weekly.")
            advice.append("Add compost or organic manure every 2-3 weeks.")

        entry = {
            "plant": plant,
            "note": note,
            "date": date,
            "advice": advice,
            "createdAt": firestore.SERVER_TIMESTAMP
        }

        db.collection("users").document(user_id).collection("growth_log").add(entry)

        return render_template("track_success.html",entry=entry)
    garden_ref = db.collection("users").document(user_id).collection("garden").stream()
    saved_plants = [doc.id for doc in garden_ref]

    return render_template('track_form.html', plants=saved_plants)

@app.route('/view-log')
def view_log():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    logs_ref = db.collection("users").document(user_id).collection("growth_log").order_by("createdAt").stream()
    logs = []
    for doc in logs_ref:
        entry = doc.to_dict()
        if "createdAt" in entry and entry["createdAt"]:
            entry["createdAt"] = entry["createdAt"].strftime("%Y-%m-%d %H:%M")
        logs.append(entry)
    
    return render_template('log.html',log=logs)

@app.route('/weather', methods=['GET','POST'])
def weather():
    mode = request.args.get('mode')

    if mode == "auto":
        city = get_user_city()
        if city:
            weather = get_weather(city)
            return render_template('weather_result.html',weather=weather)
        else:
            return "Could not auto-detect city. Please try manually."
    elif mode=="manual":
        return '''
            <form method="post">
                <label>Enter your city:</label>
                <input type="text" name="city" required>
                <button type="submit">Get Weather</button>
            </form>
                '''
    elif request.method == "POST":
        city = request.form['city']
        weather = get_weather(city)
        return render_template('weather_result.html',weather=weather)
    return redirect('/')

def get_weather(city):
    api_key = "0fc745366ffc8f7d7aadae8d4103ba9a"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return None

        temp = data["main"]["temp"]
        weather = data["weather"][0]["description"]
        advice = generate_advice(temp,weather)

        return{
            "temp" : temp,
            "description" : weather,
            "advice" : advice,
            "city" : city
        }
    
    except Exception as e:
        print("Weather error:",e)
        return None
    
def generate_advice(temp,weather):
    weather = weather.lower()
    if "rain" in weather:
        return "It is raining. No need to water your garden."
    elif temp > 32:
        return "Very hot. Water early in the morning or late evening"
    elif temp < 10:
        return "Too cold to plant anything new today."
    elif "cloud" in weather:
        return "Cloudy skies - good time for transplanting or pruning"
    elif "humid" in weather or "humidity" in weather:
        return "High humidity - be alert for pests and fungal infections"
    else:
        return "Great weather for planting and watering!"

if __name__ == "__main__":
    app.run(debug=True)