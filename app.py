import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
import PyPDF2
import docx

# Flask uygulamasını başlatıyoruz
app = Flask(__name__)

# Groq API Anahtarın
client = Groq(api_key="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")

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
        # Dosya içeriğini modele daha net bir şekilde sunalım
        file_content = f"\n\n[Sisteme Yüklenen Dosya İçeriği]:\n{extracted_text}"

    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Sen NebulaX AI'sın. Hasan Günbeyi tarafından geliştirildin. Robotik ve teknoloji uzmanısın. Sadece Türkçe cevap ver."
                },
                {
                    "role": "user", 
                    "content": user_message + file_content
                }
            ],
            model="llama-3.3-70b-versatile", # Eğer hata devam ederse "llama3-8b-8192" yapmayı dene
            temperature=0.6
        )
        
        response_text = completion.choices[0].message.content
        
        # Arayüzün beklediği JSON formatı:
        return jsonify({
            'response': response_text,
            'audio': None  # Eğer özel bir ses API'si eklemediysen None gönder, tarayıcı (TTS) okuyacaktır.
        })
        
    except Exception as e:
        # Hata olduğunda terminale hatayı yazdır ki nedenini görelim
        print(f"Hata detayı: {str(e)}")
        return jsonify({'error': str(e), 'response': 'Bağlantıda bir sorun var, API anahtarını kontrol et!'}), 500
