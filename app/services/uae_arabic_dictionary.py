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
    'Pass': 'ناجح',
    'Fail': 'فشل',
    'Passed': 'ناجح',
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
    
    # Speed One certificate exact translations
    'the term of the interior inside the vehicle are damaged': 'مصطلح الداخلية داخل المركبة متضررة',
    'the rear right light is damaged': 'الضوء الخلفي الأيمن متضرر',
    'the front lights needs to be serviced': 'الأضواء الأمامية تحتاج للصيانة',
    'there is a rust under the vehicle': 'يوجد صدأ أسفل المركبة',
    'the paint of the vehicle is damaged': 'صبغة المركبة متضررة',
    'there are scratches over all the vehicle body': 'يوجد خدوش في جسم المركبة',
    'the front left fender has been repainted': 'صبغ الجناح الأمامي اليساري',
    'the front right fender has been repainted': 'صبغ الجناح الأمامي اليميني',
    'the rear right fender is damaged': 'الجناح الخلفي اليميني متضرر',
    'the front left door has been repainted': 'صبغ الباب الأمامي اليساري',
    'the rear bumper is damaged': 'الصدامة الخلفية متضررة',
    'the engine mounting needs to be replaced': 'يجب تبديل قواعد المحرك بسبب تلف أو كسر فيها',
    
    # Common phrases from the certificate
    'damaged': 'متضرر',
    'needs to be serviced': 'تحتاج للصيانة',
    'needs to be replaced': 'يجب تبديل',
    'has been repainted': 'صبغ',
    'is damaged': 'متضرر',
    'are damaged': 'متضررة',
    'there is a rust': 'يوجد صدأ',
    'there are scratches': 'يوجد خدوش',
    'scratches': 'خدوش',
    'rust': 'صدأ',
    'vehicle': 'المركبة',
    'front': 'الأمامي',
    'rear': 'الخلفي',
    'left': 'اليساري',
    'right': 'اليميني',
    'door': 'الباب',
    'light': 'الضوء',
    'lights': 'الأضواء',
    'fender': 'الجناح',
    'bumper': 'الصدامة',
    'engine': 'المحرك',
    'mounting': 'قواعد',
    'paint': 'صبغة',
    'body': 'جسم',
    
    # Exact Arabic phrases from your list
    'pass': 'ناجح',
    'protective coating on vehicle body': 'يوجد طبقة حماية على جسم المركبة',
    'scratches on vehicle body': 'يوجد شحفات في جسم المركبة',
    'front bumper repainted': 'صبغ الدعامية الأمامية',
    'scratches on rear bumper': 'يوجد شحفات في الدعامية الخلفية',
    'engine oil leak': 'تهريب زيت بالمحرك',
    'ac compressor needs service': 'يجب صيانة كومبرسور المكيف',
    'replace front right shock': 'تبديل الجنبين الامامي اليميني',
    'replace tires': 'تبديل الإطارات',
    'replace brake pads': 'تبديل سفايف الفرامل',
    
    # Individual terms
    'oil': 'زيت',
    'leak': 'تهريب',
    'compressor': 'كومبرسور',
    'shock': 'جنبين',
    'tires': 'إطارات',
    'brake pads': 'سفايف الفرامل',
    'coating': 'طبقة حماية',
    'service': 'صيانة',
    'replace': 'تبديل',
    
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
    
    # UAE-specific automotive terms
    'needs': 'يحتاج',
    'repair': 'إصلاح', 
    'fix': 'إصلاح',
    'replace': 'تبديل',
    'service': 'صيانة',
    'check': 'فحص',
    'problem': 'مشكلة',
    'issue': 'مشكلة',
    'broken': 'مكسور',
    'cracked': 'مشقوق',
    'worn': 'مستهلك',
    'old': 'قديم',
    'new': 'جديد',
    'good': 'زين',
    'bad': 'مو زين',
    'ok': 'تمام',
    'fine': 'تمام',
    
    # More UAE automotive terms
    'half of the engine from down side is replaced': 'نصف المحرك من الجهة السفلى مستبدل',
    'rear differential repainted': 'الدفريشن الخلفي مصبوغ',
    'front differential have leak': 'الدفريشن الأمامي فيه تهريب',
    'sound with brake booster': 'صوت مع بوستر الفرامل',
    'chassis rusty': 'الشاسيه صدي',
    'car is full painted': 'السيارة مصبوغة بالكامل',
    'there is an sound in the vehicles body from underneath': 'يوجد صوت في جسم السيارة من الأسفل',
    
    # Fix differential translations
    'rear differential repainted': 'الدفريشن الخلفي مصبوغ',
    'front differential have leak': 'الدفريشن الأمامي فيه تهريب',
    'differential': 'دفريشن',
    'have leak': 'فيه تهريب',
    'repainted': 'مصبوغ',
    
    # New Arabic terms from user
    'يوجد صبغ في المركبة كاملة': 'Whole vehicle has been painted',
    'دفريشن خلفي مبطل': 'Rear differential disabled',
    'نصف ماكينة من تحت مبطل': 'Lower half of engine disabled',
    'تهريب زيت من تحت بايب الدفريشن الامامي': 'Oil leak from under front differential pipe',
    'يوجد صوت في البوستر بريك': 'There is noise in brake booster',
    'يوجد صدى في هيكل المركبه من تحت': 'There is rust in vehicle chassis from below',
    
    # English to Arabic - new terms
    'whole vehicle has been painted': 'يوجد صبغ في المركبة كاملة',
    'rear differential disabled': 'دفريشن خلفي مبطل',
    'lower half of engine disabled': 'نصف ماكينة من تحت مبطل',
    'oil leak from under front differential pipe': 'تهريب زيت من تحت بايب الدفريشن الامامي',
    'there is noise in brake booster': 'يوجد صوت في البوستر بريك',
    'there is rust in vehicle chassis from below': 'يوجد صدى في هيكل المركبه من تحت',
    'brake booster': 'البوستر بريك',
    'differential pipe': 'بايب الدفريشن',
    'disabled': 'مبطل',
    'booster': 'بوستر',
    'noise': 'صوت',
    'echo': 'صدى',
    'pipe': 'بايب',
    'from below': 'من تحت',
    'from under': 'من تحت',
    'half': 'نصف',
    'lower': 'من تحت',
    'entire': 'كاملة',
    'whole': 'كاملة',
    
    # Additional differential terms - exact case matching
    'Rear differential repainted': 'الدفريشن الخلفي مصبوغ',
    'rear differential repainted': 'الدفريشن الخلفي مصبوغ',
    'front differential have leak': 'الدفريشن الأمامي فيه تهريب',
    'Front differential have leak': 'الدفريشن الأمامي فيه تهريب',
    'differential repainted': 'الدفريشن مصبوغ',
    'differential have leak': 'الدفريشن فيه تهريب',
    'differential leak': 'تهريب الدفريشن',
}

def get_uae_arabic_translation(english_text):
    translations = {
        'Lights': 'المصابيح',
        'Body': 'الهيكل',
        'Chassis': 'الشاسي',
        'Paint': 'الصبغ',
        'Roof': 'السقف',
        'Bonnet and Trunk': 'غطاء المحرك والصندوق',
        'Fender': 'المدكار',
        'Doors': 'الأبواب',
        'Bumper and Kit': 'الدعاميات والكيت',
        'Rims': 'الرنجات',
        'Engine': 'المحرك',
        'Gear Box': 'الجير',
        'Differential': 'الدفريشن',
        '4W Drive (4x4)': 'الفور ويل (الرباعي)',
        'Transmission Shaft': 'عامود ناقل الحركة',
        'Alignment': 'الميزانيه',
        'Tyres': 'الإطارات',
        'Brakes': 'الفرامل',
        'Exhaust': 'الأكزوز'
    }
    
    return translations.get(english_text, english_text)

def translate_comment_to_arabic(comment_text):
    if not comment_text or not comment_text.strip():
        return ''
    
    original_text = comment_text.strip()
    
    # 1. Check for exact matches first (case insensitive)
    text_lower = original_text.lower()
    if text_lower in UAE_ARABIC_TERMS:
        return UAE_ARABIC_TERMS[text_lower]
    
    # Also check original case
    if original_text in UAE_ARABIC_TERMS:
        return UAE_ARABIC_TERMS[original_text]
    
    # 2. Check for partial matches in longer phrases
    for english_phrase, arabic_translation in UAE_ARABIC_TERMS.items():
        if len(english_phrase) > 10 and english_phrase.lower() in original_text.lower():
            return arabic_translation
    
    # 3. Try UAE-specific translation patterns
    translated = translate_uae_patterns(original_text)
    if translated != original_text:
        return translated
    
    # 4. Try multiple translation services with UAE context
    translated = try_translation_services(original_text)
    if translated and translated != original_text:
        return translated
    
    # 5. Word-by-word translation using comprehensive dictionary
    words = original_text.split()
    translated_words = []
    all_translated = True
    
    for word in words:
        word_clean = word.lower().strip('.,!?')
        if word_clean in UAE_ARABIC_TERMS:
            translated_words.append(UAE_ARABIC_TERMS[word_clean])
        else:
            all_translated = False
            break
    
    # Only return word-by-word if ALL words translated
    if all_translated and translated_words:
        return ' '.join(translated_words)
    
    # Final fallback - return with Arabic prefix
    return f"ملاحظة: {original_text}"

def translate_uae_patterns(text):
    """Translate using UAE automotive patterns"""
    import re
    
    text_lower = text.lower()
    
    # Pattern: "X is Y"
    if ' is ' in text_lower:
        if 'rusty' in text_lower:
            return text.replace('is rusty', 'صدي').replace('rusty', 'صدي')
        if 'painted' in text_lower:
            return text.replace('is painted', 'مصبوغ').replace('painted', 'مصبوغ')
        if 'replaced' in text_lower:
            return text.replace('is replaced', 'مستبدل').replace('replaced', 'مستبدل')
    
    # Pattern: "X have/has Y"
    if ' have ' in text_lower or ' has ' in text_lower:
        if 'leak' in text_lower:
            return text.replace('have leak', 'فيه تهريب').replace('has leak', 'فيه تهريب')
        if 'sound' in text_lower:
            return text.replace('have sound', 'فيه صوت').replace('has sound', 'فيه صوت')
    
    # Pattern: "sound with X"
    if 'sound with' in text_lower:
        return text.replace('sound with', 'صوت مع')
    
    # Pattern: "there is X"
    if text_lower.startswith('there is'):
        if 'sound' in text_lower:
            return text.replace('there is an sound', 'يوجد صوت').replace('there is a sound', 'يوجد صوت')
        if 'rust' in text_lower:
            return text.replace('there is rust', 'يوجد صدأ')
    
    return text

def try_translation_services(text):
    """Try working translation services with UAE automotive context"""
    
    # Service 1: MyMemory with UAE automotive context
    try:
        import requests
        import urllib.parse
        
        encoded_text = urllib.parse.quote(text)
        
        url = f'https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|ar&mt=1'
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; UAE-Vehicle-Inspection/1.0)'
        }
        
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if data.get('responseStatus') == 200:
                translated = data['responseData']['translatedText']
                if translated and translated != text:
                    return fix_uae_translation(translated)
    except:
        pass
    
    # Service 2: Libre Translate (if available)
    try:
        import requests
        import json
        
        url = 'https://libretranslate.de/translate'
        data = {
            'q': text,
            'source': 'en',
            'target': 'ar',
            'format': 'text'
        }
        
        response = requests.post(url, data=data, timeout=8)
        if response.status_code == 200:
            result = response.json()
            translated = result.get('translatedText', '')
            if translated and translated != text:
                return fix_uae_translation(translated)
    except:
        pass
    
    # Service 3: Google Translate (Final backup)
    try:
        import requests
        import urllib.parse
        
        encoded_text = urllib.parse.quote(text)
        url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={encoded_text}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            result = response.json()
            if result and result[0] and result[0][0]:
                translated = result[0][0][0]
                if translated and translated != text:
                    return fix_uae_translation(translated)
    except:
        pass
    
    return None

def fix_uae_translation(arabic_text):
    """Fix common translation issues for UAE automotive terms"""
    fixes = {
        'آلة': 'محرك',  # machine -> engine
        'مقاعد': 'قواعد',  # seats -> mounts
        'طبول': 'درامات',  # drums -> brake drums
        'جوانب': 'جانبينات',  # sides -> shock absorbers
        'إطارات مطاطية': 'إطارات',  # rubber tires -> tires
        'حافات': 'رنجات',  # rims
        'خدوش': 'شحفات',  # scratches (UAE term)
        'أضواء': 'لايتات',  # lights (UAE term)
        'تسرب': 'تهريب',  # leak (UAE term)
        'ضوضاء': 'صوت',  # noise -> sound (UAE term)
        'محمل': 'بيرنغ',  # bearing (UAE term)
        'مكسور': 'خربان',  # broken (UAE term)
        'صندوق التوجيه': 'بوكس ستيرنغ',  # steering box (UAE term)
    }
    
    for standard, uae in fixes.items():
        arabic_text = arabic_text.replace(standard, uae)
    
    # Remove any remaining context prefixes
    arabic_text = arabic_text.strip()
    
    # Remove common prefixes that might remain
    prefixes_to_remove = [
        'فحص المركبة الإماراتية:',
        'فحص المركبة:',
        'الإمارات العربية المتحدة:',
        'الإمارات:'
    ]
    
    for prefix in prefixes_to_remove:
        if arabic_text.startswith(prefix):
            arabic_text = arabic_text[len(prefix):].strip()
    
    return arabic_text