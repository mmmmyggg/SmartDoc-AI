from flask import Flask, request, render_template_string
import os
from werkzeug.utils import secure_filename
from pypdf import PdfReader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# HTML 页面模板（带文件上传）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>智能文档问答助手</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        input, textarea, button {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
        }
        .answer {
            background-color: #f8f9fa;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
        }
        .file-info {
            background-color: #e8f4f8;
            padding: 10px;
            margin-top: 10px;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>SmartDoc AI - 智能文档问答</h1>
        <form method="POST" enctype="multipart/form-data">
            <label>上传文档（TXT 或 PDF）：</label>
            <input type="file" name="file" accept=".txt,.pdf">
            
            <label>提问（针对文档内容）：</label>
            <textarea name="question" rows="3" placeholder="输入你的问题..."></textarea>
            
            <button type="submit">提问</button>
        </form>
        
        {% if file_info %}
        <div class="file-info">
            📄 已上传文件：{{ file_info }}
        </div>
        {% endif %}
        
        {% if answer %}
        <div class="answer">
            <strong>回答：</strong> {{ answer }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def extract_text_from_file(filepath):
    """从 TXT 或 PDF 文件中提取文本"""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    file_info = None
    
    if request.method == 'POST':
        question = request.form.get('question', '')
        file = request.files.get('file')
        
        if file and file.filename and question:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 提取文件内容
            doc_content = extract_text_from_file(filepath)
            
            if doc_content:
                file_info = f"{filename}（已提取 {len(doc_content)} 个字符）"
                # 临时：先显示提取的内容摘要，等第4天再接入 DeepSeek API
                preview = doc_content[:200] + "..." if len(doc_content) > 200 else doc_content
                answer = f"✅ 已读取文件！\n\n文件内容预览：\n{preview}\n\n你的问题是：{question}\n\n（第4天会接入 DeepSeek API 进行真正问答）"
            else:
                answer = "❌ 文件读取失败，请确保文件格式正确（TXT 或 PDF）"
    
    return render_template_string(HTML_TEMPLATE, answer=answer, file_info=file_info)

if __name__ == '__main__':
    app.run(debug=True)
