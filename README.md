# Discord Chat Bot

A Python-based Discord bot using RAG to get the transcription of the live sessions of the course [Building LLM Applications for Data Scientists and Software Engineers](https://maven.com/hugo-stefan/building-llm-apps-ds-and-swe-from-first-principles)

## Features
- Connects to Discord using the `discord` library.
- Loads a workshop transcript from a `.vtt` file for context.
- Uses OpenAI's GPT model to answer user questions based on the transcript.
- Responds to messages when called or mentioned in a Discord server.

## Getting Started

### Prerequisites
- A Discord bot token
- An OpenAI API key
- A `.env` file to store environment variables

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/sotoblanco/discord-chat-bot.git
   cd discord-chat-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   DISCORD_BOT_TOKEN=<your-discord-bot-token>
   OPENAI_API_KEY=<your-openai-api-key>
   ```

4. Place the `.vtt` transcript file in the `data/` directory and name it `WS1-C2.vtt`.

### Usage
Run the bot:
```bash
python discord_app.py
```

The bot will:
- Greet users in all text channels when it connects to a Discord server.
- Monitor messages in the server and respond to questions when called or mentioned.

## Code Overview

### Key Components
1. **Transcript Processing (`load_vtt_content`)**:
   - Reads a `.vtt` file and extracts text content while skipping metadata and timestamps.
   - Truncates the content if it exceeds the maximum character limit.

2. **OpenAI Integration (`answer_question_basic`)**:
   - Sends user questions and transcript context to OpenAI's GPT model.
   - Generates concise answers based on the transcript.

3. **Discord Bot Setup**:
   - Initializes a Discord client with appropriate intents.
   - Listens for messages and responds when called or mentioned.

4. **Web Server (`webserver.keep_alive`)**:
   - Keeps the bot running by starting a lightweight Flask server.

### File Structure
- `discord_app.py`: Main script for the Discord bot.
- `data/WS1-C2.vtt`: Workshop transcript used for context.
- `.env`: Environment variables for sensitive credentials.

## Creating a Discord bot

Go to the [Discord developer portal](https://discord.com/developers/applications) and sign in

Click on the new application and assign a name
![image](https://github.com/user-attachments/assets/07b2db08-8464-4c0a-b9aa-16f399ccbc85)

Go to the bot section and allow messages. You can assign the permissions you need for your bot. In this case, we add:

- Send messages
- Create public threads
- Send messages in threads
  
![image](https://github.com/user-attachments/assets/626dd097-5e55-4d09-9f6a-2bde86936efb)

This combination of permissions generates a combination of numbers to let you know the permission of your bot
![image](https://github.com/user-attachments/assets/7cc4bbf7-5d0d-4628-99bb-48fc3e53cc75)

Go to installation section and you will have a link provided by discord
![image](https://github.com/user-attachments/assets/a7177c9d-f227-4cb2-b827-62e7972a6511)

We need this link to add our bot to the server

The link provided by discord is: https://discord.com/oauth2/authorize?client_id=xxxxxxxxxxxxxxxxxxx

You need to add 2 more parameters:

https://discord.com/oauth2/authorize?client_id=xxxxxxxxxxxxxxxxxxx&permission=xxxxxxxxxxx&scope=bot

- ``client_id`` is provided by Discord on the link
- The ``permission`` is the combination of numbers that identify the permissions of the bot. The number for only messages is 2048, since we are adding send messages, create public threads and meesage in public threads we have this number: 309237647360
- ``scope`` the behavior that your application will have, in our case is bot

The links needs to be secret, everyone can use the bot with the link

Paste the link in your browser and it will take you to this screen in which you accept the bot and choose the server you want to added, it will let you know the permissions it has

![image](https://github.com/user-attachments/assets/9f2232bc-aa7c-48ca-90cc-f5af4284fc55)

![image](https://github.com/user-attachments/assets/85622f54-26f9-493d-b5e3-ad9378728682)

Now it's set, it will appear on your server, as we are testing a RAG application it is prompted to only answer based on the context

![image](https://github.com/user-attachments/assets/23c291fe-258f-4c8b-a8cd-ae254b11c91e)


## Deployment

Go to this website: https://render.com/

Set the repository in which you have your code

Set the requirements file and the credentials

![image](https://github.com/user-attachments/assets/c770c848-b79a-4e58-82cc-beaee3f04f7b)

To keep your bot running on your server, go to this website to monitor your bot to avoid interruptions to the service

https://uptimerobot.com/

Copy the bot link

![image](https://github.com/user-attachments/assets/e3d4238b-8da3-445f-b94d-a5f0ef8f3421)

On the uptimerobot set a new monitor and paste the link

![image](https://github.com/user-attachments/assets/980dc328-9069-4169-8ec3-4e01ac833892)


This will avoid pause in the server


## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
