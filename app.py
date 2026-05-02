import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import PyPDF2
import docx

# Flask uygulamasını başlatıyoruz
app = Flask(__name__)

# Render'dan (Environment Variables) gelen API anahtarını alıyoruz
# Eğer bulamazsa içindeki eski Groq anahtarını değil, güvenli bir hata döndürür
# API anahtarını hem VITE_ hem de GOOGLE_API_KEY olarak kontrol etsin
GEMINI_API_KEY = os.getenv("AIzaSyC8qIjPSWPawMdOL8vm6YX2CH5hm724Wnw") or os.getenv("AIzaSyC8qIjPSWPawMdOL8vm6YX2CH5hm724Wnw")

if not GEMINI_API_KEY:
    print("DİKKAT: API Anahtarı bulunamadı!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
        file_content = f"\n\n[Sisteme Yüklenen Dosya İçeriği]:\n{extracted_text}"

    try:
        # Gemini API isteği
        # Sistem talimatını (NebulaX kimliği) mesajın başına ekliyoruz
        prompt = f"Sen NebulaX AI'sın. Hasan Günbeyi tarafından geliştirildin. Robotik ve teknoloji uzmanısın. Sadece Türkçe cevap ver.\n\nKullanıcı: {user_message}{file_content}"
        
        response = model.generate_content(prompt)
        response_text = response.text
        
        return jsonify({
            'response': response_text,
            'audio': None 
        })
        
    except Exception as e:
        print(f"Hata detayı: {str(e)}")
        return jsonify({'error': str(e), 'response': 'Gemini bağlantısında bir sorun var, API anahtarını kontrol et!'}), 500

if __name__ == '__main__':
    app.run(debug=True)
