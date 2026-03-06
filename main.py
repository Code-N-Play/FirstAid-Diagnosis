from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

app = Flask(__name__)
 
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

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

    try:
        image = Image.open(file)

        prompt = """
            Analyze the injury in the image and respond ONLY in JSON format:

            {
                "injury": "",
                "risk_level": "",
                "first_aid_steps": [],
                "see_doctor_when": []
            }

            Risk level must be EXACTLY one of these values:
            HOME_CARE
            MONITOR
            DOCTOR_VISIT
            EMERGENCY 

            give short and undarstandable massege      
            """

        response = model.generate_content([prompt, image])

        # Extract text
        result_text = response.text

        # Remove markdown code blocks if Gemini adds them
        result_text = result_text.replace("```json", "").replace("```", "").strip()

        import json
        result_json = json.loads(result_text)

        return jsonify(result_json)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)