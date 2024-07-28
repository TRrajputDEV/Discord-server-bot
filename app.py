from SECRET_KEY import token
import discord
import datetime
import wikipedia
import requests
import random

# API URL for jokes
JOKE_API_URL = 'https://v2.jokeapi.dev/joke/Any'

# Random fun facts
fun_facts = [
    'Honey never spoils.',
    'A group of flamingos is called a "flamboyance".',
    'The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.',
]

# Get joke function
async def get_joke():
    response = requests.get(JOKE_API_URL)
    data = response.json()
    if data['type'] == 'single':
        return data['joke']
    else:
        return f"{data['setup']} - {data['delivery']}"

# Polls and games state
commands = {}
polls = {}
trivia = {}  # To keep track of trivia questions and answers

# client handling
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        # client.loop.create_task(self.send_daily_fact())

    async def on_message(self, message):
        # Avoid responding to the bot itself
        if message.author == self.user:
            return
        
        if message.content.lower() == 'hello':
            await message.channel.send('Hi there!')
            hour = int(datetime.datetime.now().hour)
            if hour >= 0 and hour < 12:
                await message.channel.send("Good morning ")
            elif hour >= 12 and hour < 18:
                await message.channel.send("Good Afternoon ")
            else:
                await message.channel.send("Good Evening ")
            await message.channel.send('How you doing ')
            
        elif message.content.lower() == 'how are you?':
            await message.channel.send('I am a bot, but I am doing great! How about you?')
        elif message.content.lower() == 'bye':
            await message.channel.send('Goodbye! Have a great day!')
        elif 'what is' in message.content.lower() or 'tell me about' in message.content.lower():
            query = message.content.lower().replace('what is', '').replace('tell me about', '').strip()
            if query:
                try:
                    summary = wikipedia.summary(query, sentences=1)
                    await message.channel.send(f'Here is what I found: {summary}')
                except wikipedia.exceptions.DisambiguationError as e:
                    await message.channel.send(f"Disambiguation error. Please be more specific. Suggestions: {e.options[:5]}")
                except wikipedia.exceptions.PageError:
                    await message.channel.send("Sorry, I couldn't find any information on that topic.")
                except Exception as e:
                    await message.channel.send(f"An error occurred: {str(e)}")
            else:
                await message.channel.send("Please provide a topic to search for.")
        elif 'fun fact' in message.content.lower():
            fact = random.choice(fun_facts)
            await message.channel.send(fact)
        elif 'joke' in message.content.lower():
            joke = await get_joke()
            await message.channel.send(joke)
        elif message.content.startswith('!addcommand'):
            parts = message.content.split(' ', 2)
            if len(parts) == 3:
                command_name = parts[1]
                response_text = parts[2]
                commands[command_name] = response_text
                await message.channel.send(f'Custom command !{command_name} added.')
            else:
                await message.channel.send('Usage: !addcommand <command_name> <response>')
        elif message.content.startswith('!'):
            command_name = message.content[1:]
            if command_name in commands:
                await message.channel.send(commands[command_name])
        elif message.content.startswith('!poll'):
            parts = message.content.split(' ', 2)
            if len(parts) == 3:
                poll_question = parts[1]
                poll_options = parts[2].split(',')
                options_text = "\n".join([f"{i+1}. {opt.strip()}" for i, opt in enumerate(poll_options)])
                poll_message = await message.channel.send(f"Poll: {poll_question}\n{options_text}")
                for i in range(len(poll_options)):
                    await poll_message.add_reaction(str(i+1))
                polls[poll_message.id] = {str(i+1): 0 for i in range(len(poll_options))}
            else:
                await message.channel.send('Usage: !poll <question> <option1,option2,...>')
        elif message.content.startswith('!trivia'):
            trivia_questions = {
                'What is the capital of France?': 'Paris',
                'What is the largest planet in our solar system?': 'Jupiter'
            }
            question = random.choice(list(trivia_questions.keys()))
            trivia['question'] = question
            trivia['answer'] = trivia_questions[question]
            await message.channel.send(f"Trivia Question: {question}")
        elif message.content.startswith('!answer'):
            answer = message.content[len('!answer '):].strip()
            correct_answer = trivia.get('answer')
            if answer.lower() == correct_answer.lower():
                await message.channel.send("Correct!")
            else:
                await message.channel.send(f"Incorrect! The correct answer was: {correct_answer}")

    async def on_reaction_add(self, reaction, user):
        if reaction.message.id in polls:
            if reaction.emoji in polls[reaction.message.id]:
                polls[reaction.message.id][reaction.emoji] += 1
                

# Intent setup
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(token)
