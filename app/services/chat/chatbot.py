import os
import json
import openai
import asyncio
import aiohttp
from dotenv import load_dotenv
from typing import List, Dict, Optional
from .chatbot_schema import chat_request, chat_response, HistoryItem
from app.utils.knowledge.knowledge import knowledge_manager
from app.utils.cache_manager import cache_manager

load_dotenv()

class Chat:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.product_api_base = "api.pantallaverde.com/api/v1/products"

    async def get_response(self, request: chat_request, id: str) -> chat_response:
        # Get history: use provided history or fetch from cache
        history = request.history
        if not history and id:
            history = cache_manager.get_history(id)
        
        # First AI response to determine if vectordb search is needed
        analysis_result = self.analyze_message(request.message, history)

        # Validate analysis result format
        if not isinstance(analysis_result, dict):
            return chat_response(
                response="I apologize, but I'm having trouble processing your request. Please try again.",
                user_message=request.message
            )

        if analysis_result.get("vector_search") == True:
            # Vector search is needed
            vector_query = analysis_result.get("vector_query", "")
            user_language = analysis_result.get("language", "english")
            
            if vector_query:  # Only search if we have a valid query
                relevant_products = self.search_relevant_products(vector_query)
                
                if relevant_products:
                    relevant_products = await self.enrich_products_with_stock(relevant_products)
            else:
                relevant_products = []
            
            response_text = self.generate_response_with_products(
                request.message, 
                relevant_products,
                user_language,
                history
            )
        else:
            response_text = analysis_result.get("response", "I'm sorry, I couldn't understand your request.")

        if id:
            cache_manager.update_history(id, request.message, response_text, history)
        
        return chat_response(
            response=response_text,
            user_message=request.message
        )
    
    def analyze_message(self, message: str, history: Optional[List[HistoryItem]] = None) -> dict:
        """
        You are an AI shopping assistant for Pantalla Verde, an e-commerce store specializing in [specify products: electronics, clothing, etc.].

CORE RULES:
1. ONLY answer questions related to e-commerce, shopping, products, orders, and customer service
2. For off-topic requests, politely redirect: "I can only help with shopping and product questions at Pantalla Verde. How can I assist you with your purchase today?"

RESPONSE WORKFLOW:

STEP 1 - CHECK CONVERSATION HISTORY FIRST:
- Review recent messages to see if relevant product information was ALREADY retrieved via vector search
- If the user is asking follow-up questions about products already discussed, USE THE EXISTING CONTEXT
- Examples of follow-up questions that DON'T need new search:
  * "What about the battery life?" (when product was just discussed)
  * "Does it come in blue?" (referring to previously mentioned item)
  * "How does that compare to the other one?" (comparing already-fetched products)
  * "Tell me more about its features" (product already in context)
  * "Is that one better?" (referring to products in recent history)

STEP 2 - DETERMINE IF NEW VECTOR SEARCH IS NEEDED:

USE vector search when:
- User asks about NEW products not yet discussed
- User changes topic to different product category
- User requests fresh product recommendations
- No relevant product information exists in recent history

SKIP vector search when:
- User asks follow-up questions about products already retrieved
- User asks about policies (shipping, returns, warranty)
- User asks for clarification on already-discussed products
- Greeting/general questions
- Order tracking, account issues

If VECTOR SEARCH needed:
1. Generate a clear, concise English search query (2-8 words)
2. Focus on key product attributes: type, brand, features, category
3. Set vector_search: true
4. Leave response empty (will be filled after search)

If NO vector search needed:
1. Provide a helpful direct response using conversation history
2. Set vector_search: false
3. Leave vector_query empty

ALWAYS:
- Detect the user's language and respond in the same language
- Keep responses friendly, concise, and helpful
- Use the user's exact message as user_msg

EXAMPLES:

Conversation History: [User asked about wireless headphones, vector search returned Sony WH-1000XM5]
User: "What's the battery life on those?"
→ vector_search: false, response: "The Sony WH-1000XM5 headphones offer up to 30 hours of battery life...", language: "en"

Conversation History: [Just discussed laptops]
User: "actually, show me gaming mice instead"
→ vector_search: true, vector_query: "gaming mice", language: "en"

Conversation History: Empty
User: "looking for wireless headphones under $100"
→ vector_search: true, vector_query: "wireless headphones budget affordable", language: "en"

Conversation History: [Discussed return policy]
User: "what about shipping?"
→ vector_search: false, response: "Our shipping policy...", language: "en"

Conversation History: [Vector search returned 3 gaming laptops]
User: "which one has the best graphics card?"
→ vector_search: false, response: "Among the laptops we just discussed, the [model] has the best graphics card...", language: "en"

OUTPUT FORMAT:
{
    "vector_search": bool,
    "vector_query": str or "",
    "response": str or "",
    "language": str,
    "user_msg": str
}
        """
        # Prepare conversation context
        history_context = ""
        if history:
            recent_history = history[-8:] if len(history) > 8 else history
            history_context = "\n".join([f"User: {h.message}\nAssistant: {h.response}" for h in recent_history])
        else:
            history_context = "No prior conversation"

        prompt = f"""
        Analyze the user's message and conversation history to determine if a product database (vector) search is required.

        Current user message:
        "{message}"

        Recent conversation history:
        {history_context}

        Your task:
        1. Detect the language of the message.
        2. Determine if a vector (product) search is needed based on whether the user:
        - Asks about specific products, features, comparisons, prices, or availability
        - Requests recommendations or follows up on product discussions
        3. If a vector search is needed:
        - Return an English search query summarizing the product-related intent
        - Include the detected language
        4. If a vector search is NOT needed:
        - Write a helpful, polite response in the **same language** as the user's message
        - Leave vector_query empty

        Respond in strict JSON format:
        {{
            "vector_search": true or false,
            "vector_query": "string (empty if not needed)",
            "language": "detected language name",
            "response": "LLM response if no vector search, empty otherwise",
            "user_msg": "{message}"
        }}
        """


        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an intent classifier and response generator that outputs only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=250
            )

            # Parse model output
            import json
            result_text = completion.choices[0].message.content.strip()
            result = json.loads(result_text)
            return result

        except Exception as e:
            print(f"Error in analyze_message: {e}")
            return {
                "vector_search": False,
                "vector_query": "",
                "language": "unknown",
                "response": "Sorry, I couldn't process your message right now.",
                "user_msg": message
            }

    
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

    
    def generate_response_with_products(self, original_message: str, products: List[Dict], user_language: str, history: Optional[List[HistoryItem]] = None) -> str:
        """Generate a response with products in the user's original language"""
        
        messages = [{"role": "system", "content": self.get_system_prompt_with_products(products, user_language, history)}]
        messages.append({"role": "user", "content": original_message})
        
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
    
    def get_system_prompt_with_products(self, products: List[Dict], user_language: str, history: Optional[List[HistoryItem]] = None) -> str:
        """Generate system prompt for responses with products"""
        context = self.format_product_context_with_stock(products)
        
        history_text = ""
        if history:
            recent_history = history[-8:] if len(history) > 8 else history
            history_text = "\n".join([f"User: {h.message}\nAssistant: {h.response}" for h in recent_history])
        else:
            history_text = "No prior history."
        
        return f"""You are a helpful e-commerce assistant with access to real-time inventory.
        
        Available products in our store:
        {context}
        
        User's conversation history:
        {history_text}
        
        IMPORTANT: The user's message language is detected as: {user_language}
        You MUST respond in {user_language}.
        
        Guidelines for your response:
        1. Answer the user's specific question directly and naturally in {user_language}
        2. Reference conversation history when relevant to provide context
        3. Only mention stock status, prices, or features when specifically asked or when comparing
        4. Be conversational and helpful without being pushy or promotional
        5. Keep responses focused and concise
        6. ALWAYS respond in {user_language} - this is critical"""
    
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
