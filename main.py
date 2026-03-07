from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import json
import re

app = Flask(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=API_KEY)

# Load model
model = genai.GenerativeModel("gemini-2.5-flash")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/symptom')
def symptom():
    return render_template('symptom.html')


@app.route('/analyze', methods=['POST'])
def analyze():

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"})

    file = request.files['image']

    if file.filename == "":
        return jsonify({"error": "No selected image"})

    try:

        image = Image.open(file.stream).convert("RGB")

        prompt = """
You are a medical first aid assistant.

Analyze the injury in the image.

Return ONLY valid JSON.

{
"injury": "",
"risk_level": "",
"first_aid_steps": [],
"see_doctor_when": []
}

Risk level must be exactly one of:
HOME_CARE
MONITOR
DOCTOR_VISIT
EMERGENCY

Keep language simple for normal people.
"""

        response = model.generate_content([prompt, image])

        result_text = response.text

        # Extract JSON safely
        match = re.search(r'\{.*\}', result_text, re.S)

        if match:
            result_json = json.loads(match.group())
        else:
            raise Exception("Invalid JSON response")

        return jsonify(result_json)

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "injury": "Unable to analyze image",
            "risk_level": "MONITOR",
            "first_aid_steps": ["Upload a clearer image"],
            "see_doctor_when": []
        })

@app.route('/analyze_symptom', methods=['POST'])
def analyze_symptom():

    try:

        data = request.get_json()

        symptoms = data.get("symptoms", [])
        body_parts = data.get("body_parts", [])
        duration = data.get("duration", [])
        age = data.get("age", [])

        print("Symptoms:", symptoms)
        print("Body Parts:", body_parts)
        print("Duration:", duration)
        print("Age:", age)

        if not symptoms and not body_parts:
            return jsonify({
                "injury": "No symptoms selected",
                "risk_level": "MONITOR",
                "first_aid_steps": ["Please select symptoms"],
                "see_doctor_when": []
            })

        prompt = f"""

        You are a medical first aid assistant.

            User injured body part: {body_parts}

            User symptoms: {symptoms}

            injury duration: {duration}

            injured persons age: {age}

            Identify the possible injury and give first aid advice.

            Respond ONLY in JSON format:

            
            {{
                "injury": "",
                "risk_level": "",
                "first_aid_steps": [],
                "see_doctor_when": []
            }}

            Risk level must be EXACTLY one of:

            HOME_CARE
            MONITOR
            DOCTOR_VISIT
            EMERGENCY

            Keep advice short and easy to understand.
            """

        response = model.generate_content(prompt)

        result_text = response.text

        # Clean Gemini formatting
        result_text = result_text.replace("```json", "").replace("```", "").strip()

        print("Gemini response:", result_text)

        try:
            result_json = json.loads(result_text)
        except:
            result_json = {
                "injury": "Unable to analyze symptoms",
                "risk_level": "MONITOR",
                "first_aid_steps": ["Try selecting more symptoms"],
                "see_doctor_when": []
            }

        return jsonify(result_json)

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "injury": "Server error",
            "risk_level": "MONITOR",
            "first_aid_steps": ["Please try again"],
            "see_doctor_when": []
        })


# =========================
# Run App
# =========================
if __name__ == '__main__':
    app.run(debug=True)