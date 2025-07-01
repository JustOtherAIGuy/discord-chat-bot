import gradio as gr
import json
import os
from datetime import datetime

class EvalApp:
    def __init__(self, data_file='eval/questions.json', progress_file='eval/eval_progress.json'):
        self.data_file = data_file
        self.progress_file = progress_file
        self.data = self.load_data()
        self.progress = self.load_progress()
        self.current_index = self.progress.get('current_index', 0)
        
    def load_data(self):
        """Load evaluation data from JSON file"""
        data = []
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return data
                
                # Handle both line-by-line JSON and concatenated JSON
                if content.startswith('['):
                    # It's a JSON array
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError:
                        pass
                else:
                    # It's either line-by-line or concatenated JSON objects
                    lines = content.split('\n')
                    if len(lines) == 1:
                        # Concatenated JSON objects on one line
                        # Split by '}{'  and add back the braces
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
                        # Line-by-line JSON
                        for line in lines:
                            line = line.strip()
                            if line:
                                try:
                                    data.append(json.loads(line))
                                except json.JSONDecodeError:
                                    continue
        return data
    
    def load_progress(self):
        """Load evaluation progress"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'current_index': 0, 'evaluations': {}}
    
    def save_progress(self):
        """Save evaluation progress"""
        os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def get_current_question(self):
        """Get current question data"""
        if self.current_index < len(self.data):
            return self.data[self.current_index]
        return None
    
    def evaluate_question(self, evaluation, notes):
        """Save evaluation for current question"""
        if self.current_index < len(self.data):
            question_id = str(self.current_index)
            self.progress['evaluations'][question_id] = {
                'evaluation': evaluation,
                'notes': notes,
                'timestamp': datetime.now().isoformat()
            }
            self.progress['current_index'] = self.current_index
            self.save_progress()
    
    def next_question(self):
        """Move to next question"""
        if self.current_index < len(self.data) - 1:
            self.current_index += 1
            self.progress['current_index'] = self.current_index
            self.save_progress()
    
    def previous_question(self):
        """Move to previous question"""
        if self.current_index > 0:
            self.current_index -= 1
            self.progress['current_index'] = self.current_index
            self.save_progress()
    
    def get_progress_info(self):
        """Get progress information"""
        total = len(self.data)
        if total == 0:
            return "No questions loaded"
        current = self.current_index + 1
        evaluated = len(self.progress['evaluations'])
        remaining = total - current
        return f"Question {current}/{total} | Evaluated: {evaluated} | Remaining: {remaining}"
    
    def get_current_evaluation(self):
        """Get current evaluation if exists"""
        question_id = str(self.current_index)
        if question_id in self.progress['evaluations']:
            return self.progress['evaluations'][question_id]
        return {'evaluation': None, 'notes': ''}

# Initialize the app
eval_app = EvalApp()

# Check if data exists
if not eval_app.data:
    print("Warning: No evaluation data found in eval/eval_retrieval_questions.json")
    print("Please run the evaluation script first to generate data.")

def update_display():
    """Update the display with current question"""
    question_data = eval_app.get_current_question()
    current_eval = eval_app.get_current_evaluation()
    
    if question_data is None:
        return "No more questions!", "", "", eval_app.get_progress_info(), ""
    
    question = question_data['question']
    response = question_data['response']
    context_info = json.dumps(question_data.get('context_info', {}), indent=2)
    progress = eval_app.get_progress_info()
    notes = current_eval.get('notes', '')
    
    return question, response, context_info, progress, notes

def pass_evaluation(notes):
    """Mark current question as pass"""
    eval_app.evaluate_question('pass', notes)
    eval_app.next_question()
    return update_display()

def fail_evaluation(notes):
    """Mark current question as fail"""
    eval_app.evaluate_question('fail', notes)
    eval_app.next_question()
    return update_display()

def skip_question():
    """Skip current question without evaluation"""
    eval_app.next_question()
    return update_display()

def go_previous():
    """Go to previous question"""
    eval_app.previous_question()
    return update_display()

def jump_to_question(question_num):
    """Jump to specific question number"""
    if 1 <= question_num <= len(eval_app.data):
        eval_app.current_index = question_num - 1
        eval_app.progress['current_index'] = eval_app.current_index
        eval_app.save_progress()
    return update_display()

# Create Gradio interface
with gr.Blocks(title="Retrieval Evaluation Tool") as demo:
    gr.Markdown("# Retrieval Evaluation Tool")
    gr.Markdown("Evaluate retrieval responses with pass/fail ratings and notes.")
    
    with gr.Row():
        with gr.Column(scale=2):
            progress_display = gr.Textbox(
                label="Progress", 
                interactive=False,
                value=eval_app.get_progress_info()
            )
            
            question_display = gr.Textbox(
                label="Question", 
                interactive=False,
                max_lines=5
            )
            
            response_display = gr.Textbox(
                label="Response", 
                interactive=False,
                max_lines=10
            )
            
            with gr.Accordion("Context Info (Optional)", open=False):
                context_display = gr.Code(
                    label="Context Information",
                    language="json",
                    interactive=False
                )
            
            notes_input = gr.Textbox(
                label="Notes",
                placeholder="Add your evaluation notes here...",
                max_lines=5
            )
            
            with gr.Row():
                pass_btn = gr.Button("✅ Pass", variant="primary")
                fail_btn = gr.Button("❌ Fail", variant="stop")
                skip_btn = gr.Button("⏭️ Skip", variant="secondary")
        
        with gr.Column(scale=1):
            gr.Markdown("### Navigation")
            
            prev_btn = gr.Button("⬅️ Previous")
            
            with gr.Row():
                jump_input = gr.Number(
                    label="Jump to Question #",
                    minimum=1,
                    maximum=max(1, len(eval_app.data)),
                    step=1,
                    value=1
                )
                jump_btn = gr.Button("Go")
            
            gr.Markdown("### Export Progress")
            export_btn = gr.Button("📁 Export Results")
            export_output = gr.File(label="Download Results", visible=False)
    
    # Event handlers
    pass_btn.click(
        pass_evaluation,
        inputs=[notes_input],
        outputs=[question_display, response_display, context_display, progress_display, notes_input]
    )
    
    fail_btn.click(
        fail_evaluation,
        inputs=[notes_input],
        outputs=[question_display, response_display, context_display, progress_display, notes_input]
    )
    
    skip_btn.click(
        skip_question,
        outputs=[question_display, response_display, context_display, progress_display, notes_input]
    )
    
    prev_btn.click(
        go_previous,
        outputs=[question_display, response_display, context_display, progress_display, notes_input]
    )
    
    jump_btn.click(
        jump_to_question,
        inputs=[jump_input],
        outputs=[question_display, response_display, context_display, progress_display, notes_input]
    )
    
    def export_results():
        """Export evaluation results"""
        results_file = f"eval/evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        # Create summary report
        total_evaluated = len(eval_app.progress['evaluations'])
        passed = sum(1 for eval_data in eval_app.progress['evaluations'].values() 
                    if eval_data['evaluation'] == 'pass')
        failed = sum(1 for eval_data in eval_app.progress['evaluations'].values() 
                    if eval_data['evaluation'] == 'fail')
        
        export_data = {
            'summary': {
                'total_questions': len(eval_app.data),
                'total_evaluated': total_evaluated,
                'passed': passed,
                'failed': failed,
                'pass_rate': passed / total_evaluated if total_evaluated > 0 else 0
            },
            'evaluations': eval_app.progress['evaluations'],
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(results_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return gr.File(value=results_file, visible=True)
    
    export_btn.click(
        export_results,
        outputs=[export_output]
    )
    
    # Initialize display
    demo.load(
        update_display,
        outputs=[question_display, response_display, context_display, progress_display, notes_input]
    )

if __name__ == "__main__":
    demo.launch(share=True) 