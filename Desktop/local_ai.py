import ollama
# send a prompt directly to your local Llama 3 model
response = ollama.chat(
	model='llama3',
	messages=[
		{
			'role': 'user',
			'content': 'Explain how a local AI engine works in one punchy sentence .'
		}
	]
)

#print the model's output straight to your terminal
print(response['message']['content'])