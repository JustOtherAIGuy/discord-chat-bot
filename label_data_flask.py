from flask import Flask, request, redirect, render_template_string
import json
import os
from datetime import datetime

QUESTIONS_FILE = 'eval/eval_retrieval_questions.json'
PROGRESS_FILE = 'eval/eval_progress.json'

app = Flask(__name__)

def load_questions():
    if not os.path.exists(QUESTIONS_FILE):
        return []
    with open(QUESTIONS_FILE, 'r') as f:
        content = f.read().strip()
        if not content:
            return []
        if content.startswith('['):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return []
        else:
            data = []
            lines = content.split('\n')
            if len(lines) == 1:
                json_strings = content.split('}{')
                for i, json_str in enumerate(json_strings):
                    if i == 0:
                        json_str += '}'
                    elif i == len(json_strings) - 1:
                        json_str = '{' + json_str
                    else:
                        json_str = '{' + json_str + '}'
                    try:
                        data.append(json.loads(json_str))
                    except json.JSONDecodeError:
                        continue
            else:
                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            return data

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'current_index': 0, 'evaluations': {}}

def save_progress(progress):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Minimal Eval App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        .question-box { border: 1px solid #ccc; padding: 1em; margin-bottom: 1em; }
        .context { background: #f9f9f9; padding: 0.5em; font-size: 0.95em; }
        .reviewed { color: green; }
    </style>
</head>
<body>
    <h2>Question {{ idx+1 }}/{{ total }}</h2>
    <div class="question-box">
        <strong>Q:</strong> {{ question.get('question', '') }}<br>
        <strong>Response:</strong> {{ question.get('response', '') }}<br>
        {% if question.get('context_info') %}
        <div class="context"><strong>Context:</strong><br><pre>{{ question.get('context_info')|tojson(indent=2) }}</pre></div>
        {% endif %}
        {% if eval_data %}
        <div class="reviewed">[Already reviewed: {{ eval_data['evaluation'] }}] Notes: {{ eval_data.get('notes','') }}</div>
        {% endif %}
    </div>
    <form method="post">
        <label>Notes:<br><textarea name="notes" rows="2" cols="60">{{ eval_data.get('notes','') if eval_data else '' }}</textarea></label><br><br>
        <button name="action" value="pass">✅ Pass</button>
        <button name="action" value="fail">❌ Fail</button>
        <button name="action" value="skip">⏭️ Skip</button>
        <button name="action" value="back">⬅️ Previous</button>
    </form>
    <p>Progress: {{ idx+1 }}/{{ total }} | Evaluated: {{ evaluated }} | Remaining: {{ total-idx-1 }}</p>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    questions = load_questions()
    if not questions:
        return '<h3>No questions to review.</h3>'
    progress = load_progress()
    idx = progress.get('current_index', 0)
    total = len(questions)
    if request.method == 'POST':
        action = request.form.get('action')
        notes = request.form.get('notes', '')
        if action in ['pass', 'fail']:
            progress['evaluations'][str(idx)] = {
                'evaluation': action,
                'notes': notes,
                'timestamp': datetime.now().isoformat()
            }
            progress['current_index'] = idx
            save_progress(progress)
            idx += 1
        elif action == 'skip':
            idx += 1
        elif action == 'back':
            idx = max(0, idx-1)
        progress['current_index'] = idx
        save_progress(progress)
        return redirect('/')
    if idx >= total:
        return '<h3>Review complete! All questions reviewed.</h3>'
    question = questions[idx]
    eval_data = progress['evaluations'].get(str(idx), {})
    evaluated = len(progress['evaluations'])
    return render_template_string(TEMPLATE, question=question, idx=idx, total=total, eval_data=eval_data, evaluated=evaluated)

if __name__ == '__main__':
    app.run(debug=True)
