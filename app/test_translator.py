#!/usr/bin/env python3

def test_translator():
    print("Testing translator...")
    
    try:
        import translators as ts
        print("✓ Translators library imported successfully")
        
        # Test basic translation
        test_text = "Hello world"
        result = ts.translate_text(test_text, translator='bing', from_language='en', to_language='ar')
        print(f"✓ Translation successful: '{test_text}' -> '{result}'")
        
        # Test automotive terms
        automotive_tests = [
            "Front left headlight not working",
            "passenger door scratch", 
            "Lights",
            "Engine"
        ]
        
        for text in automotive_tests:
            try:
                result = ts.translate_text(text, translator='bing', from_language='en', to_language='ar')
                print(f"✓ '{text}' -> '{result}'")
            except Exception as e:
                print(f"✗ Failed to translate '{text}': {e}")
                
    except ImportError:
        print("✗ Translators library not found")
    except Exception as e:
        print(f"✗ Translation failed: {e}")

if __name__ == "__main__":
    test_translator()