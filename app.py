from flask import Flask, request, render_template_string
import os
from werkzeug.utils import secure_filename
from pypdf import PdfReader
from openai import OpenAI

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# DeepSeek 客户端
client = OpenAI(
    api_key="sk-a75baa4a88484f4193125043fb9dbed8",  # 替换成你真实的 DeepSeek API Key
    base_url="https://api.deepseek.com"
)

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
            white-space: pre-wrap;
        }
        .file-info {
            background-color: #e8f4f8;
            padding: 10px;
            margin-top: 10px;
            border-radius: 4px;
            font-size: 14px;
        }
        .loading {
            color: #007bff;
            font-style: italic;
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
            📄 {{ file_info }}
        </div>
        {% endif %}

        {% if loading %}
        <div class="loading">🤔 AI 正在思考中...</div>
        {% endif %}

        {% if answer %}
        <div class="answer">
            <strong>💡 回答：</strong><br>{{ answer }}
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


def ask_deepseek(question, context):
    """调用 DeepSeek API 回答问题"""
    # 如果文档内容太长，截断前 4000 字符（避免超过 API 限制）
    if len(context) > 4000:
        context = context[:4000] + "\n...(内容过长，已截断)"

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system",
             "content": f"你是一个专业的文档问答助手。请根据以下文档内容回答用户的问题。如果问题无法从文档中找到答案，请说'文档中没有相关信息'。"},
            {"role": "user", "content": f"文档内容：\n{context}\n\n用户问题：{question}"}
        ],
        stream=False
    )

    return response.choices[0].message.content


@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    file_info = None
    loading = False

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
                loading = True

                # 调用 DeepSeek API
                answer = ask_deepseek(question, doc_content)
            else:
                answer = "❌ 文件读取失败，请确保文件格式正确（TXT 或 PDF）"

    return render_template_string(HTML_TEMPLATE, answer=answer, file_info=file_info, loading=loading)


if __name__ == '__main__':
    app.run(debug=True)