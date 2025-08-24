import os
import json
import openai
from dotenv import load_dotenv
from .ai_suggestions_schema import ai_suggestions_request, ai_suggestions_response

load_dotenv ()

class Suggestion():
    def __init__(self):
        self.client=openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_suggestion(self, input_data:str)->ai_suggestions_request:
        prompt=self.create_prompt()
        data=input_data
        response=self.get_openai_response (prompt,data)
        return response
    
    def create_prompt(self) -> str:
        return f"""You are an expert at creating ADHD-friendly summaries. Your job is to take complex text and make it clear, organized, and easy to process.

                **ADHD-FRIENDLY FORMATTING RULES:**
                - Use short paragraphs (2-3 sentences max)
                - Include bullet points and numbered lists
                - Add clear headings and subheadings
                - Use bold text for key information
                - Break up long blocks of text

                **SUMMARY STRUCTURE:**
                1. **Main Point** (1-2 sentences): What is this about?
                2. **Key Details** (bullet points): The most important information
                3. **Action Items** (if any): What should the reader do?
                4. **Bottom Line** (1 sentence): The takeaway message

                **WRITING STYLE:**
                - Use simple, direct language
                - Avoid jargon and complex terms
                - Keep sentences short (under 20 words when possible)
                - Use active voice
                - Include transition words like "First," "Next," "Finally"

                **FOCUS GUIDELINES:**
                - Highlight the most important 3-5 points
                - Remove unnecessary details and tangents
                - Group related information together
                - Use numbers and concrete examples
                - Make it scannable for quick reading

                Now summarize the following text using these guidelines:

                [TEXT TO SUMMARIZE GOES HERE]"""
                
    def get_openai_response (self, prompt:str, data:str)->str:
        completion =self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"system", "content": prompt},{"role":"user", "content": data}],
            temperature=0.7            
        )
        return completion.choices[0].message.content
    



