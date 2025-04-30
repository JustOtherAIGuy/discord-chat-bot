from openai import OpenAI
import asyncio
import os
from discord_app import load_vtt_content, answer_question_basic, MAX_CHARS

client_openai = OpenAI()

async def main(message_content):
    transcript_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "WS1-C2.vtt")  # Add the path to your transcript file
    workshop_context = load_vtt_content(transcript_file)
    original_length = len(workshop_context)
    if original_length > MAX_CHARS:
        workshop_context = workshop_context[:MAX_CHARS]

    response = await answer_question_basic(client_openai, workshop_context, message_content)
    return response

if __name__ == "__main__":
    questions = open("data/eval/questions.txt", "r").readlines()
    responses = []
    for question in questions:
        print(f"Question: {question.strip()}")
        response = asyncio.run(main(question.strip()))
        responses.append(response)

    print("\n\nResponses:\n\n")
    for response in responses:
        print(response)

    # use pandas to save question and response as a tsv
    import pandas as pd
    df = pd.DataFrame({"Question": questions, "Response": responses})
    # add a uuid to the filename
    import uuid
    df.to_csv(f"data/eval/responses_{uuid.uuid4()}.tsv", sep="\t", index=False)