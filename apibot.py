import os
import google.generativeai as genai


genai.configure(api_key="AIzaSyDxwWdelWz61PNzKFCsOYLXWvxk0IiCJOA")

model = genai.GenerativeModel('gemini-1.5-flash')


while(True):
    question= input("You:")

    if(question.strip() ==''):
        break

    response = model.generate_content(question)
    print('\n')
    print(f"Bot: {response.text}")
    print('\n')