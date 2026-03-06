from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Gemini API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


@app.route('/')
def home():
    return render_template('index.html')


# Image analyze route
@app.route('/analyze', methods=['POST'])
def analyze():

    if 'image' not in request.files:
        return jsonify({"result": "No image uploaded"})

    file = request.files['image']

    try:
        image = Image.open(file)

        prompt = """
You are a medical first aid assistant.

Look at the injury image and respond in this format:

Possible Injury:
Risk Level (Low/Moderate/High):
First Aid Steps:
When should the user see a doctor?

Keep the answer simple so normal people can understand.
"""

        response = model.generate_content([prompt, image])

        return jsonify({
            "result": response.text
        })

    except Exception as e:
        return jsonify({"result": str(e)})


if __name__ == '__main__':
    app.run(debug=True)