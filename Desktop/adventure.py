import ollama

print("=== LOCAL OFFLINE TEXT ADVENTURE ===")
print("Type 'exit' to quit.\n")

# Dynamic system prompt to prevent repetitive scenarios like picking up a lamp
messages = [
    {
        'role': 'system', 
        'content': 'You are a dynamic, unpredictable text-based adventure engine. Never repeat the same cliché scenario like entering a building to pick up a lamp. Create entirely unique, sprawling worlds (sci-fi, cyberpunk, fantasy, or post-apocalyptic) with diverse choices, hazards, and unexpected events. Always present the current situation vividly and end by asking the player what they want to do.'
    }
]

while True:
    user_input = input("\nWhat do you want to do? > ")
    if user_input.lower() == 'exit':
        break

    # Add player's action to the conversation history
    messages.append({'role': 'user', 'content': user_input})

    # Get response from your local Llama 3 model
    response = ollama.chat(model='llama3.2:1b', messages=messages)
    
    # Extract and print the story response
    reply = response['message']['content']
    print(f"\n{reply}")

    # Add the AI's response to the history so it maintains context
    messages.append({'role': 'assistant', 'content': reply})
