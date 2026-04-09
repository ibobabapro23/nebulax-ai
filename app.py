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
    
    if file:
        file_content = "\n[Dosya İçeriği]: " + read_file(file)

    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Sen NebulaX AI'sın. Hasan Günbeyi tarafından geliştirildin. "
                        "Robotik, yazılım ve teknoloji konularında yardımcı olan bir asistansın. "
                        "Sadece Türkçe ve anlaşılır bir dille cevap ver. "
                        "Asla garip karakterler veya yabancı dillerden semboller kullanma. "
                        "Hasan Günbeyi ismini sadece geliştiricin sorulduğunda belirt."
                    )
                },
                {
                    "role": "user", 
                    "content": user_message + file_content
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            top_p=0.9
        )
        
        response_text = completion.choices[0].message.content
        return jsonify({'response': response_text})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)