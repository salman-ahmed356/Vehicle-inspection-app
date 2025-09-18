"""
UAE Arabic Dictionary for Automotive Terms
Based on local UAE inspection certificates
"""

UAE_ARABIC_TERMS = {
    # Main expertise types
    'Paint': 'صبغ',
    'Body': 'هيكل',
    'Engine': 'محرك',
    'Brake': 'فرامل',
    'Brakes': 'فرامل',
    'Suspension': 'نظام التعليق',
    'Interior': 'داخلية',
    'Exterior': 'خارجية',
    'Mechanical': 'ميكانيكية',
    'ECU': 'وحدة التحكم الإلكترونية',
    'Road': 'طريق',
    
    # Vehicle parts - Complete list from inspection items
    'Chassis': 'شاسيه',
    'Lights': 'أضواء',
    'Roof': 'سقف',
    'Doors': 'أبواب',
    'Fender': 'جناح',
    'Bumper': 'صدام',
    'Bumper and Kit': 'صدام وكت',
    'Rims': 'جنوط',
    'Gear Box': 'جير',
    'Differential': 'ديفرنشل',
    'Bonnet and Trunk': 'كبوت وصندوق',
    '4W Drive (4x4)': 'دفع رباعي',
    'Transmission Shaft': 'عمود النقل',
    'Alignment': 'ضبط الاتجاه',
    'Tyres': 'إطارات',
    'Exhaust': 'عادم',
    
    # Additional terms from PDF
    'Additional to Body': 'إضافات الهيكل',
    'Notes And More Details': 'ملاحظات وتفاصيل أكثر',
    'INSPECTION RESULTS': 'نتائج الفحص',
    
    # Status terms
    'Pass': 'نجح',
    'Fail': 'فشل',
    'Passed': 'نجح',
    'Failed': 'فشل',
    'Good': 'جيد',
    'Bad': 'سيء',
    'Damaged': 'متضرر',
    'Repainted': 'معاد طلاؤه',
    
    # Common phrases
    'Comment': 'ملاحظة',
    'Note': 'ملاحظة',
    'Terms & Conditions': 'الشروط والأحكام',
    'Inspection Results': 'نتائج الفحص',
    
    # Common automotive phrases from PDF - UAE dialect
    'damaged': 'متضرر',
    'needs to be serviced': 'يحتاج صيانة',
    'needs to be replaced': 'يحتاج تبديل',
    'needs replacement': 'يحتاج تبديل',
    'needs service': 'يحتاج صيانة',
    'has been repainted': 'مصبوغ',
    'are damaged': 'متضررة',
    'is damaged': 'متضرر',
    'scratches': 'خدوش',
    'rust': 'صدأ',
    'interior': 'داخلية',
    'vehicle': 'مركبة',
    'front': 'أمامي',
    'rear': 'خلفي',
    'left': 'يسار',
    'right': 'يمين',
    'door': 'باب',
    'light': 'ضوء',
    'mounting': 'تركيب',
    'not working': 'ما يشتغل',
    'scratch': 'خدش',
    'dent': 'انبعاج',
    'loose': 'مفكوك',
    'are loose': 'مفكوكة',
    'belts are loose': 'الأحزمة مفكوكة',
    'electrical issues': 'مشاكل كهربائية',
    'electrical issues in door': 'مشاكل كهربائية في الباب',
    'passenger door scratch': 'خدش باب الراكب',
    'front left headlight not working': 'الضوء الأمامي الأيسر ما يشتغل',
    'blinker not working': 'الغماز ما يشتغل',
    'dent on front fender': 'انبعاج في الجناح الأمامي',
    'front chassis damaged': 'الشاسيه الأمامي متضرر',
    'rear chassis scratch': 'خدش الشاسيه الخلفي',
    'passenger door repainted': 'باب الراكب مصبوغ',
    'bootlid repainted': 'غطاء الصندوق مصبوغ',
    'engine hood repainted': 'غطاء المحرك مصبوغ',
    'belts are loose': 'الأحزمة مفكوكة',
    
    # Individual words for better translation
    'headlight': 'ضوء أمامي',
    'blinker': 'غماز',
    'passenger': 'راكب',
    'chassis': 'شاسيه',
    'repainted': 'مصبوغ',
    'bootlid': 'غطاء الصندوق',
    'hood': 'غطاء',
    'fender': 'جناح',
    'electrical': 'كهربائي',
    'issues': 'مشاكل',
    'belts': 'أحزمة',
    'working': 'يشتغل',
}

def get_uae_arabic_translation(english_text):
    translations = {
        'Lights': 'أضواء',
        'Body': 'هيكل',
        'Chassis': 'شاسيه', 
        'Paint': 'صبغ',
        'Roof': 'سقف',
        'Bonnet and Trunk': 'كبوت وصندوق',
        'Fender': 'جناح',
        'Doors': 'أبواب',
        'Bumper and Kit': 'صدام وكت',
        'Rims': 'جنوط',
        'Engine': 'محرك',
        'Gear Box': 'جير',
        'Differential': 'ديفرنشل',
        '4W Drive (4x4)': 'دفع رباعي',
        'Transmission Shaft': 'عمود النقل',
        'Alignment': 'ضبط الاتجاه',
        'Tyres': 'إطارات',
        'Brakes': 'فرامل',
        'Exhaust': 'عادم'
    }
    
    return translations.get(english_text, english_text)

def translate_comment_to_arabic(comment_text):
    if not comment_text or not comment_text.strip():
        return ''
    
    original_text = comment_text.strip()
    
    # Check for exact matches first
    if original_text.lower() in UAE_ARABIC_TERMS:
        return UAE_ARABIC_TERMS[original_text.lower()]
    
    # Try multiple translation services
    translated = try_translation_services(original_text)
    if translated and translated != original_text:
        return translated
    
    # Fallback to word-by-word translation using local dictionary
    words = original_text.split()
    translated_words = []
    translation_found = False
    
    for word in words:
        word_clean = word.lower().strip('.,!?')
        if word_clean in UAE_ARABIC_TERMS:
            translated_words.append(UAE_ARABIC_TERMS[word_clean])
            translation_found = True
        else:
            translated_words.append(word)
    
    # If some translation occurred, return mixed result
    if translation_found:
        return ' '.join(translated_words)
    
    # Final fallback - return with Arabic prefix
    return f"ملاحظة: {original_text}"

def try_translation_services(text):
    """Try multiple translation services in order of reliability"""
    
    # Service 1: MyMemory (Free, no API key needed)
    try:
        import requests
        url = f'https://api.mymemory.translated.net/get?q={text}&langpair=en|ar'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('responseStatus') == 200:
                translated = data['responseData']['translatedText']
                if translated and translated != text:
                    return translated
    except Exception as e:
        print(f"MyMemory translation failed: {e}")
    
    # Service 2: LibreTranslate (Free, open source)
    try:
        import requests
        url = 'https://libretranslate.de/translate'
        data = {
            'q': text,
            'source': 'en',
            'target': 'ar',
            'format': 'text'
        }
        response = requests.post(url, data=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            translated = result.get('translatedText', '')
            if translated and translated != text:
                return translated
    except Exception as e:
        print(f"LibreTranslate failed: {e}")
    
    # Service 3: Google Translate (Unofficial API)
    try:
        import requests
        import urllib.parse
        
        encoded_text = urllib.parse.quote(text)
        url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={encoded_text}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result and result[0] and result[0][0]:
                translated = result[0][0][0]
                if translated and translated != text:
                    return translated
    except Exception as e:
        print(f"Google Translate failed: {e}")
    
    # Service 4: Lingva Translate (Alternative Google frontend)
    try:
        import requests
        import urllib.parse
        url = f'https://lingva.ml/api/v1/en/ar/{urllib.parse.quote(text)}'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            translated = data.get('translation', '')
            if translated and translated != text:
                return translated
    except Exception as e:
        print(f"Lingva Translate failed: {e}")
    
    return None