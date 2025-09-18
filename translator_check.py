#!/usr/bin/env python3
"""
Check which translation services work on VPS
"""

import requests
import urllib.parse

def test_mymemory(text):
    try:
        url = f'https://api.mymemory.translated.net/get?q={text}&langpair=en|ar'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('responseStatus') == 200:
                return data['responseData']['translatedText']
        return None
    except Exception as e:
        print(f"MyMemory error: {e}")
        return None

def test_libretranslate(text):
    try:
        url = 'https://libretranslate.de/translate'
        data = {
            'q': text,
            'source': 'en',
            'target': 'ar',
            'format': 'text'
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get('translatedText', '')
        return None
    except Exception as e:
        print(f"LibreTranslate error: {e}")
        return None

def test_google_translate(text):
    try:
        encoded_text = urllib.parse.quote(text)
        url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={encoded_text}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result and result[0] and result[0][0]:
                return result[0][0][0]
        return None
    except Exception as e:
        print(f"Google Translate error: {e}")
        return None

def test_lingva_translate(text):
    try:
        url = f'https://lingva.ml/api/v1/en/ar/{urllib.parse.quote(text)}'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('translation', '')
        return None
    except Exception as e:
        print(f"Lingva Translate error: {e}")
        return None

def main():
    test_phrases = [
        "engine needs repair",
        "front door damaged", 
        "electrical problem"
    ]
    
    services = [
        ("MyMemory", test_mymemory),
        ("LibreTranslate", test_libretranslate), 
        ("Google Translate", test_google_translate),
        ("Lingva Translate", test_lingva_translate)
    ]
    
    print("Testing Translation Services")
    print("=" * 40)
    
    for phrase in test_phrases:
        print(f"\nTesting: '{phrase}'")
        print("-" * 25)
        
        for service_name, service_func in services:
            result = service_func(phrase)
            if result and result != phrase:
                print(f"✓ {service_name}: {result}")
            else:
                print(f"✗ {service_name}: Failed")

if __name__ == "__main__":
    main()