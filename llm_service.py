import requests
import json
import time
import threading
from collections import defaultdict
import re

# Default to Ollama, but this can be swapped for other LLM services
LLM_PROVIDER = "ollama"

# Simple rate limiting
class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period  # in seconds
        self.calls = defaultdict(list)
        self.lock = threading.Lock()
    
    def can_call(self, key="default"):
        with self.lock:
            now = time.time()
            # Clean old calls
            self.calls[key] = [call_time for call_time in self.calls[key] if now - call_time < self.period]
            
            # Check if we can make a new call
            if len(self.calls[key]) < self.max_calls:
                self.calls[key].append(now)
                return True
            return False
    
    def wait_until_can_call(self, key="default"):
        while not self.can_call(key):
            time.sleep(0.1)

# Initialize rate limiter: 3 calls per 5 seconds
rate_limiter = RateLimiter(max_calls=3, period=5)

def get_available_models():
    """
    Get a list of available models based on the LLM provider.
    """
    if LLM_PROVIDER == "ollama":
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = [model["name"] for model in response.json().get("models", [])]
                return models if models else ["codellama"]
            else:
                return ["codellama"]  # Default
        except Exception:
            return ["codellama"]  # Default
    else:
        return ["default_model"]

def analyze_code(code_snippet, model="codellama"):
    """
    Analyze a code snippet using the configured LLM provider.
    
    Args:
        code_snippet (str): The code to analyze
        model (str): The model to use
        
    Returns:
        tuple: (analysis_text, metrics_dict)
    """
    if LLM_PROVIDER == "ollama":
        return _analyze_with_ollama(code_snippet, model)
    elif LLM_PROVIDER == "another_provider":
        # Placeholder for other providers
        return _analyze_with_another_provider(code_snippet)
    else:
        return "LLM provider not supported", {"error": "Provider not supported"}

def estimate_token_count(text):
    """
    Rough estimate of token count based on whitespace and punctuation.
    This is a simple approximation - actual tokenization varies by model.
    """
    # Split on whitespace and punctuation
    tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
    return len(tokens)

def _analyze_with_ollama(code_snippet, model="codellama"):
    """
    Use Ollama to analyze code with improved error handling and metrics.
    Ollama must be running locally (default at http://localhost:11434).
    """
    # Apply rate limiting
    rate_limiter.wait_until_can_call(model)
    
    metrics = {
        "model": model,
        "input_tokens": estimate_token_count(code_snippet),
        "output_tokens": 0,
        "latency": "0.00 seconds"
    }
    
    prompt = f"""
    Please analyze and explain the following code:
    
    ```
    {code_snippet}
    ```
    
    Provide a clear explanation of what the code does, its structure, 
    and any notable patterns or potential issues. Include:
    
    1. Overall purpose of the code
    2. Breakdown of key functions/components
    3. Potential bugs or edge cases
    4. Performance considerations
    """
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Lower temperature for more focused responses
                        "num_predict": 2048  # Maximum tokens to generate
                    }
                },
                timeout=60
            )
            
            end_time = time.time()
            metrics["latency"] = f"{end_time - start_time:.2f} seconds"
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "No analysis provided")
                
                # Update metrics
                metrics["output_tokens"] = estimate_token_count(analysis)
                
                return analysis, metrics
                
            elif response.status_code == 404:
                if "model" in response.text.lower():
                    raise Exception(f"Model '{model}' not found. Please select another model.")
                else:
                    raise Exception(f"API endpoint not found. Is Ollama running?")
                    
            elif response.status_code == 429:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception("Rate limit exceeded. Please try again later.")
                    
            else:
                raise Exception(f"API error (Status code: {response.status_code}): {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception("Could not connect to Ollama. Please make sure Ollama is running locally.")
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                raise Exception("Request timed out. The model may be overloaded or unavailable.")
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                raise e

def _analyze_with_another_provider(code_snippet):
    """
    Placeholder for integrating with another LLM provider.
    Implementation details would go here.
    """
    # This would be implemented when adding a new provider
    return "Provider not yet implemented", {"error": "Provider not implemented"}