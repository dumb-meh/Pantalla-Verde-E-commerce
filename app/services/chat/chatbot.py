import os
import json
import openai
from dotenv import load_dotenv
from typing import List, Dict
from .chatbot_schema import chat_request, chat_response
from app.utils.knowledge import knowledge_manager

load_dotenv()

class Chat:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_response(self, request: chat_request) -> chat_response:
        user_intent = self.analyze_user_intent(request.message)
        relevant_products = self.search_relevant_products(user_intent)
        response_text = self.generate_response(request.message, user_intent, relevant_products)
        
        return chat_response(response=response_text)
    
    def analyze_user_intent(self, message: str) -> str:
        """Analyze user intent and translate if necessary"""
        prompt = """Analyze the following user message and extract the key intent.
        If the message is not in English, translate it to English first.
        Focus on identifying:
        1. Product names or types they're asking about
        2. Specific features or specifications
        3. Price inquiries
        4. Availability questions
        
        Return a concise English search query that captures the main intent.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-search-preview",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
                max_tokens=100
            )
            return completion.choices[0].message.content
        except Exception as e:
            return message 
    
    def search_relevant_products(self, query: str) -> List[Dict]:
        """Search for relevant products in the vector database"""
        try:
            products = knowledge_manager.search_products(query, n_results=3)
            return products
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def generate_response(self, original_message: str, intent: str, products: List[Dict]) -> str:
        """Generate a response based on products found or general knowledge"""
        
        if products:
            context = self.format_product_context(products)
            prompt = f"""You are a helpful e-commerce assistant. 
            A customer asked: "{original_message}"
            
            Based on our store inventory, here are the relevant products:
            {context}
            
            Provide a helpful response in the same language as the customer's message.
            Be informative and suggest the products naturally.
            If they ask about price, mention the prices.
            If they ask about availability, confirm what's in stock.
            Keep the response conversational and helpful."""
        else:
            prompt = f"""You are a helpful e-commerce assistant.
            A customer asked: "{original_message}"
            
            This specific product is not available in our store currently.
            However, provide helpful general information about what they're asking for.
            
            IMPORTANT:
            1. First mention that we don't have this specific item in stock
            2. Then provide general helpful information about the topic
            3. Do NOT include any website references, URLs, or external links
            4. Do NOT mention specific stores or competitors
            5. Keep the response helpful and informative
            6. Respond in the same language as the customer's message"""
        
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": original_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "I apologize, but I'm having trouble processing your request. Please try again later."
    
    def format_product_context(self, products: List[Dict]) -> str:
        """Format product information for context"""
        context_parts = []
        
        for i, product in enumerate(products, 1):
            data = product.get('data', {})
            parts = [f"\nProduct {i}:"]
            
            if data.get('productName'):
                parts.append(f"- Name: {data['productName']}")
            if data.get('brand'):
                parts.append(f"- Brand: {data['brand']}")
            if data.get('model'):
                parts.append(f"- Model: {data['model']}")
            if data.get('price'):
                parts.append(f"- Price: ${data['price']}")
            if data.get('priceWithInstallation'):
                parts.append(f"- Price with installation: ${data['priceWithInstallation']}")
            if data.get('description'):
                parts.append(f"- Description: {data['description']}")
            if data.get('status'):
                parts.append(f"- Availability: {data['status']}")
            if data.get('warrantyType'):
                parts.append(f"- Warranty: {data['warrantyType']}")
            
            context_parts.append("\n".join(parts))
        
        return "\n".join(context_parts)