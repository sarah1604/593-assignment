pip install google-generativeai
import google.generativeai as genai
genai.configure(
api_key=API_KEY
)
model=genai.GenerativeModel('gemini-pro')
chat=model.start_chat(history=[])
while(True):
question= input("You:")
response=chat.send_message(question)
print('\n')
print(f"Bot: {response.text}")
print('\n')
if(question.strip() ==''):
break