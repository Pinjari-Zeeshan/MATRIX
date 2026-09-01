import ollama

response = ollama.chat(
    model='qwen2.5:3b',
    messages=[
        {'role': 'user', 'content': 'Say "MATRIX brain online" and nothing else.'}
    ]
)

print(response['message']['content'])