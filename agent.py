import os
import json
from openai import OpenAI
from upstash_vector import Index
from dotenv import load_dotenv

load_dotenv()

class PortfolioAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.index = Index(
            url=os.getenv("UPSTASH_VECTOR_REST_URL"),
            token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        )
        
        self.model = "gpt-4.1-nano" 

    def search_knowledge_base(self, query):
        """Tool: Recherche des infos dans le portfolio via Upstash"""
        try:
            results = self.index.query(
                data=query, 
                top_k=3, 
                include_data=True
            )
            context = "\n".join([res.data for res in results])
            return context if context else "Aucune info trouvée."
        except Exception as e:
            return str(e)

    def get_response(self, messages):
        tools = [{
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "Cherche des informations sur le parcours, les projets ou les compétences de Théo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Sujet à rechercher"}
                    },
                    "required": ["query"]
                }
            }
        }]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            
            for tool_call in msg.tool_calls:
                if tool_call.function.name == "search_knowledge_base":
                    args = json.loads(tool_call.function.arguments)
                    context = self.search_knowledge_base(args["query"])
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": context
                    })
            
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return final_response.choices[0].message.content, messages
        
        return msg.content, messages