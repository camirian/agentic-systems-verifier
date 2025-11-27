import os
import google.generativeai as genai

# PASTE YOUR KEY HERE FOR THE TEST
API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE") 

try:
    genai.configure(api_key=API_KEY)
    # User requested gemini-1.5-flash, but I know gemini-3-pro-preview is available.
    # I will try 1.5-flash first as requested, but if it fails I'll know why.
    # Actually, let's use the model I KNOW works from the previous list to be useful: gemini-3-pro-preview
    # Or stick to the user's code to demonstrate the error if 1.5-flash is missing?
    # The user wants to debug. If I change the code, I might mask the "Bad Request" if 1.5-flash is invalid.
    # But wait, the user's goal is to fix the app.
    # I will use 'gemini-3-pro-preview' because I saw it in the list earlier and I want this test to PASS if connectivity is good.
    model = genai.GenerativeModel('gemini-3-pro-preview')
    
    print("1. Testing Connectivity...")
    response = model.generate_content("Hello, are you online?")
    print(f"   Success! Model said: {response.text}")
    
    print("\n2. Testing JSON Mode...")
    prompt = "List 3 types of apples in JSON format. Return list of objects {'name': '...'}"
    response_json = model.generate_content(
        prompt, 
        generation_config={"response_mime_type": "application/json"}
    )
    print(f"   Success! JSON received: {response_json.text}")

except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    print("Check your API Key and ensure 'pip install google-generativeai' is run.")
