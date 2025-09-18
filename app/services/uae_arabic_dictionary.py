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
    
    # First check local UAE dictionary for common phrases
    comment_lower = comment_text.lower().strip()
    for eng_phrase, ar_phrase in UAE_ARABIC_TERMS.items():
        if eng_phrase.lower() in comment_lower:
            comment_lower = comment_lower.replace(eng_phrase.lower(), ar_phrase)
    
    # If we found local translations, return the mixed result
    if comment_lower != comment_text.lower().strip():
        return comment_lower
    
    try:
        import requests
        import urllib.parse
        
        # Force UAE Arabic dialect with multiple parameters
        text = urllib.parse.quote(comment_text.strip())
        # Use UAE-specific parameters: tl=ar (Arabic), hl=ar-AE (UAE region), gl=AE (country)
        url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&hl=ar-AE&gl=AE&dt=t&dt=bd&ie=UTF-8&oe=UTF-8&q={text}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ar-AE,ar;q=0.9,en;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result and result[0] and result[0][0]:
                translated_text = result[0][0][0]
                if translated_text and translated_text.strip():
                    return translated_text.strip()
    except Exception as e:
        print(f"Translation error for '{comment_text}': {e}")
    
    # Fallback to original text
    return comment_text