import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import PyPDF2
import docx

# ÇOK KRİTİK: Flask uygulamasını burada başlatıyoruz
app = Flask(__name__)

# API anahtarını doğrudan buraya, tırnak içine yapıştır
GEMINI_API_KEY = "AIzaSyC8qIjPSWPawMdOL8vm6YX2CH5hm724Wnw"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def read_file(file):
    if not file or file.filename == '':
        return ""
    filename = file.filename
    try:
        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        elif filename.endswith('.docx'):
            doc = docx.Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        elif filename.endswith('.txt'):
            return file.read().decode('utf-8')
    except Exception as e:
        return f"Dosya okunurken hata oluştu: {str(e)}"
    return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.form.get('message', '')
    file = request.files.get('file')
    file_content = ""
    
    if file and file.filename != '':
        extracted_text = read_file(file)
        file_content = f"\n\n[Dosya]:\n{extracted_text}"

    try:
        prompt = f"Sen NebulaX AI'sın. Hasan Günbeyi tarafından geliştirildin. Robotik uzmanısın. Türkçe cevap ver.\n\nKullanıcı: {user_message}{file_content}"
        response = model.generate_content(prompt)
        
        return jsonify({
            'response': response.text,
            'audio': None 
        })
    except Exception as e:
        return jsonify({'error': str(e), 'response': 'Gemini bağlantı hatası!'}), 500

if __name__ == '__main__':
    app.run(debug=True)
