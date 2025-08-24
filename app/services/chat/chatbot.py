import os
import json
import openai
from dotenv import load_dotenv
from .chatbot_schema import chat_request, chat_response

load_dotenv ()

class Chat():
    def __init__(self):
        self.client=openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_suggestion(self, input_data:str)->chat_request:
        prompt=self.create_prompt()
        data=input_data
        response=self.get_openai_response (prompt,data)
        return response
    
    def create_prompt(self) -> str:
        return f"""You are an expert conversational AI for e-commerce website for customer suggestions.
        Given the user message, generate a relevant and helpful response to assist the customer."""
                
    def get_openai_response (self, prompt:str, data:str)->str:
        completion =self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"system", "content": prompt},{"role":"user", "content": data}],
            temperature=0.7            
        )
        return completion.choices[0].message.content
    



