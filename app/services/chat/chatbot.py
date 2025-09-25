import os
import json
import openai
import asyncio
import aiohttp
from dotenv import load_dotenv
from typing import List, Dict, Optional
from .chatbot_schema import chat_request, chat_response, HistoryItem
from app.utils.knowledge.knowledge import knowledge_manager

load_dotenv()

class Chat:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.product_api_base = "api.pantallaverde.com/api/v1/products"
    
    async def get_response(self, request: chat_request) -> chat_response:
        user_intent = self.analyze_user_intent(request.message)
        
        relevant_products = self.search_relevant_products(user_intent)
        
        if relevant_products:
            relevant_products = await self.enrich_products_with_stock(relevant_products)
        
        response_text = self.generate_response(
            request.message, 
            user_intent, 
            relevant_products,
            request.history
        )
        
        return chat_response(
            response=response_text,
            user_message=request.message
        )
    
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
                model="gpt-4o-mini",
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
            products = knowledge_manager.search_products(query, n_results=5)
            return products
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    async def fetch_single_product_stock(self, session: aiohttp.ClientSession, product_id: str) -> Dict:
        """Fetch stock information for a single product"""
        try:
            url = f"{self.product_api_base}/{product_id}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "id": product_id,
                        "totalStock": data.get("totalStock", 0),
                        "data": data
                    }
                else:
                    return {
                        "id": product_id,
                        "totalStock": None,
                        "error": f"API returned status {response.status}"
                    }
        except asyncio.TimeoutError:
            return {
                "id": product_id,
                "totalStock": None,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "id": product_id,
                "totalStock": None,
                "error": str(e)
            }
    
    async def enrich_products_with_stock(self, products: List[Dict]) -> List[Dict]:
        """Enrich products with real-time stock information"""
        enriched_products = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for product in products:
                product_id = product.get('id')
                if product_id:
                    tasks.append(self.fetch_single_product_stock(session, product_id))
            
            if tasks:
                stock_results = await asyncio.gather(*tasks)
                
                stock_dict = {result['id']: result for result in stock_results}
                
                for product in products:
                    product_id = product.get('id')
                    if product_id and product_id in stock_dict:
                        stock_info = stock_dict[product_id]
                        if 'data' not in product:
                            product['data'] = {}
                        product['data']['totalStock'] = stock_info.get('totalStock')
                    enriched_products.append(product)
            else:
                enriched_products = products
        
        return enriched_products

    
    def generate_response(self, original_message: str, intent: str, products: List[Dict], history: Optional[List[HistoryItem]] = None) -> str:
        """Generate a response based on products found or general knowledge"""
        
        messages = [{"role": "system", "content": self.get_system_prompt(products,history)}]
        
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "I apologize, but I'm having trouble processing your request. Please try again later."
    
    def get_system_prompt(self, products: List[Dict],history) -> str:
        """Generate system prompt based on whether products were found"""
        if products:
            context = self.format_product_context_with_stock(products)
            return f"""You are a helpful e-commerce assistant with access to real-time inventory.
            
            Based on our store inventory, here are the relevant products with current stock information:
            {context}
            
            Here is user past conversation history: {history if history else 'No prior history.'}
            
            Provide helpful responses that:
            1. Mention product availability and stock status
            2. Suggest products naturally based on the query
            3. Include prices when relevant
            4. Highlight if items are low in stock or out of stock
            5. Be conversational and helpful
            6. Respond in the same language as the customer's message"""
        else:
            return """You are a helpful e-commerce assistant.
            
            The specific product being asked about is not available in our store currently.
            
            IMPORTANT:
            1. First mention that we don't have this specific item in stock or maybe there is an error in the system why we can't find it
            2. Then provide general helpful information about the topic
            3. Do NOT include any website references, URLs, or external links
            4. Do NOT mention specific stores or competitors
            5. Keep the response helpful and informative
            6. Respond in the same language as the customer's message"""
    
    def format_product_context_with_stock(self, products: List[Dict]) -> str:
        """Format product information with stock details for context"""
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
            
            total_stock = data.get('totalStock')
            stock_status = data.get('stockStatus', 'unknown')
            
            if total_stock is not None:
                if stock_status == 'out_of_stock':
                    parts.append(f"- Stock: OUT OF STOCK")
                elif stock_status == 'low_stock':
                    parts.append(f"- Stock: LOW STOCK ({total_stock} units remaining)")
                elif stock_status == 'in_stock':
                    parts.append(f"- Stock: IN STOCK ({total_stock} units available)")
            else:
                parts.append(f"- Stock: Status unavailable")
            
            if data.get('description'):
                parts.append(f"- Description: {data['description']}")
            if data.get('warrantyType'):
                parts.append(f"- Warranty: {data['warrantyType']}")
            
            context_parts.append("\n".join(parts))
        
        return "\n".join(context_parts)
