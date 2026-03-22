import requests
import json
import base64

class OpenRouterEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.5-flash"
        self.memory = {}

    def get_answer(self, user_id, query, chunks):
        """Processes text queries using RAG context and Chat Memory."""
        if user_id not in self.memory:
            self.memory[user_id] = []

        context_text = "\n".join([f"Source: {c['source']}\n{c['text']}" for c in chunks])

        messages = [
            {"role": "system", "content": f"Context:\n{context_text}\n\nAnswer based ONLY on the context. If unknown, say so."}
        ]
        
        
        messages.extend(self.memory[user_id][-4:])
        messages.append({"role": "user", "content": query})

        response = requests.post(
            url=self.url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            data=json.dumps({
                "model": self.model,
                "messages": messages,
                "max_tokens": 800
            })
        )
        
        result = response.json()
        if 'choices' in result:
            answer = result['choices'][0]['message']['content']
            
            self.memory[user_id].append({"role": "user", "content": query})
            self.memory[user_id].append({"role": "assistant", "content": answer})
            return answer
        return "Error: Could not reach the AI Engine."

    def get_image_description(self, user_id, image_path): 
        """Multimodal logic: Strictly provides a short caption and 3 tags."""
        if user_id not in self.memory:
            self.memory[user_id] = []

        with open(image_path, "rb") as img:
            b64_img = base64.b64encode(img.read()).decode('utf-8')
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a concise vision assistant. Your output must follow this EXACT format:\n"
                        "Caption: [Insert a short caption . No conversational fillers or detailed description]\n"
                        "Tags:\n"
                        "1. [Tag 1]\n"
                        "2. [Tag 2]\n"
                        "3. [Tag 3]"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image with a short caption and 3 tags."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]
                }
            ],
            "max_tokens": 500 
        }

        response = requests.post(
            url=self.url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        result = response.json()
        
        if 'choices' in result:
            description = result['choices'][0]['message']['content']
            self.memory[user_id].append({"role": "assistant", "content": f"Image Analysis: {description}"})
            return description
        return "Vision analysis failed. Please try again."
       

    def summarize_chat(self, user_id):
        """Summarizes the recent conversation and image analysis for the user."""

        if user_id not in self.memory or not self.memory[user_id]:
            return "I don't have any recent messages in my memory to summarize yet!"


        history = self.memory[user_id][-6:]
        history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history])
        
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Summarize the key points of the conversation provided, including any image analysis and policy answers, in 2-3 concise bullet points."},
                {"role": "user", "content": f"Please summarize this recent chat history:\n{history_text}"}
            ],
            "max_tokens": 400
        }

        response = requests.post(
            url=self.url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        result = response.json()
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        return "Sorry, I couldn't generate a summary at this time."