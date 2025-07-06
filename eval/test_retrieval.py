import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vector_emb import answer_question, llm_answer_question, get_openai_client

import pandas as pd
import numpy as np
import json

df = pd.read_json('eval/questions.json')

questions = np.unique(df['question'].values)

client = get_openai_client()
for question in questions:
    context, sources, chunks = answer_question(question)
    response, context_info = llm_answer_question(client, context, sources, chunks, question)
    # store metadata in a json file in eval folder
    with open('eval/qa_pairs.json', 'a') as f:
        json.dump([{
            'question': question,
            'response': response,
          #  'context_info': context_info
        }], f)
    print(response)
    print(context_info)
    print("-"*100 + "\n")




