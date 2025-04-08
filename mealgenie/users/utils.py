import requests
import json
import ollama 

def prompt_ollama(prompt, model="llama3.2", system_prompt=None, temperature=0.7):
    """
    Send a prompt to an Ollama model and get the response.
    Returns:
        str: The model's response
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature
    }
    
    if system_prompt:
        payload["system"] = system_prompt
        
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        result = response.json()
        return result["response"]
        
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return None