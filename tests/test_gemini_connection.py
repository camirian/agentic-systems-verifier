import google.generativeai as genai
import os

api_key = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")

def test_gemini():
    print(f"Configuring with API Key: {api_key[:5]}...")
    genai.configure(api_key=api_key)
    
    print("Listing available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
        
    print("\nTesting gemini-2.0-pro...")
    try:
        model = genai.GenerativeModel('gemini-2.0-pro')
        response = model.generate_content("Hello, are you there?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-2.0-pro: {e}")

    print("\nTesting gemini-1.5-pro...")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content("Hello, are you there?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-1.5-pro: {e}")

if __name__ == "__main__":
    test_gemini()
