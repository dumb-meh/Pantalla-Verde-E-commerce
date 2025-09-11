import os
import json
import openai
from dotenv import load_dotenv
from .ai_suggestions_schema import ai_suggestions_request, ai_suggestions_response

load_dotenv()

class Suggestion:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_suggestion(self, request: ai_suggestions_request) -> ai_suggestions_response:
        prompt = self.create_prompt()
        data = self.format_input_data(request)
        response_text = self.get_openai_response(prompt, data)
        response_dict = json.loads(response_text)
        return ai_suggestions_response(**response_dict)
    
    def format_input_data(self, request: ai_suggestions_request) -> str:
        return f"""
        Product Name: {request.product_name}
        Brand: {request.brand}
        Model: {request.model}
        """
    
    def create_prompt(self) -> str:
        return """You are an expert e-commerce product description generator.
        Given the product details, generate a compelling product description, competitive pricing, and relevant tags.
        
        IMPORTANT RULES:
        1. Create original, engaging product descriptions without referencing any external websites
        2. Suggest realistic market prices based on the product type and brand
        3. Generate relevant tags for search optimization
        4. Do not include any URLs, website references, or external links
        5. Focus only on the product features and benefits
        6. Respond only in JSON format as specified below no extra text, no markdowns
        {
            "description": "Detailed product description here",
            "price": "Suggested price in USD",
            "tags": "comma-separated relevant tags"
        }"""
                
    def get_openai_response(self, prompt: str, data: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini-search-preview",  
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": data}
            ]
        )
        return completion.choices[0].message.content
    
