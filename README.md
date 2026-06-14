from flask import Flask, request, render_template_string

app = Flask(__name__)

# 极简版 HTML 页面模板
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
        input, button {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #007bff;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .answer {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>SmartDoc AI - 智能文档问答</h1>
        <form method="POST">
            <input type="text" name="question" placeholder="输入你的问题..." required>
            <button type="submit">提问</button>
        </form>
        {% if answer %}
        <div class="answer">
            <strong>回答：</strong> {{ answer }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    if request.method == 'POST':
        question = request.form.get('question', '')
        if question:
            # 临时：先返回一个简单的回复，等第4天再接入 DeepSeek API
            answer = f"你问的是：{question}。等第4天会接入 DeepSeek API！"
    return render_template_string(HTML_TEMPLATE, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
