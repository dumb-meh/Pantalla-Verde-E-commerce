import os
import json
import openai
from dotenv import load_dotenv
from .ai_suggestions_schema import ai_suggestions_request, ai_suggestions_response
from pydantic import ValidationError
from fastapi import HTTPException

load_dotenv()

class Suggestion:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_suggestion(self, request: ai_suggestions_request) -> ai_suggestions_response:
        prompt = self.create_prompt()
        data = self.format_input_data(request)
        response_text = self.get_openai_response(prompt, data)

        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            cleaned_json = response_text[json_start:json_end]

            response_dict = json.loads(cleaned_json)
            return ai_suggestions_response(**response_dict)

        except (json.JSONDecodeError, ValidationError, TypeError) as e:
            print("Error parsing JSON:", e)
            raise HTTPException(status_code=500, detail="AI response was not in expected format.")
    
    def format_input_data(self, request: ai_suggestions_request) -> str:
        return f"""
        Product Name: {request.product_name}
        Brand: {request.brand}
        Model: {request.model}
        """
    
    def create_prompt(self) -> str:
        return """You are an expert e-commerce product description generator.

Generate a compelling product description, a realistic competitive price in USD, and relevant SEO-friendly tags from the product details.

STRICT RULES:
1. Output MUST be a valid JSON object only - no markdown, no explanations, no extra text.
2. Do NOT include any external links or references.
3. The JSON object MUST follow this exact structure:
{
"description": "string",
"price": "string",
"tags": "string (comma-separated)"
}

Example:
{
"description": "A beautiful and high-performing 4K TV...",
"price": "$499.99",
"tags": "4K, television, smart TV, UHD, 55-inch, home entertainment"
}

Now generate the JSON object based on the following product details:
"""
     
    def get_openai_response(self, prompt: str, data: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini-search-preview",  
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": data}
            ]
        )
        return completion.choices[0].message.content
    
