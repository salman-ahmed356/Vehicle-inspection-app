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
    
    # Common automotive phrases from PDF - Missing translations added
    'damaged': 'متضرر',
    'needs to be serviced': 'يحتاج للصيانة',
    'needs to be replaced': 'يحتاج للاستبدال',
    'needs replacement': 'يحتاج للاستبدال',
    'needs service': 'يحتاج للصيانة',
    'has been repainted': 'تم إعادة طلائه',
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
    'not working': 'لا يعمل',
    'scratch': 'خدش',
    'dent': 'انبعاج',
    'loose': 'مفكوك',
    'are loose': 'مفكوكة',
    'belts are loose': 'الأحزمة مفكوكة',
    'electrical issues': 'مشاكل كهربائية',
    'electrical issues in door': 'مشاكل كهربائية في الباب',
    'passenger door scratch': 'خدش باب الراكب',
    'Front left headlight not working': 'الضوء الأمامي الأيسر لا يعمل',
    'blinker not working': 'الغماز لا يعمل',
    'dent on front fender': 'انبعاج في الجناح الأمامي',
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
    
    try:
        import requests
        import urllib.parse
        
        # Direct HTTP request to Google Translate
        text = urllib.parse.quote(comment_text.strip())
        url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={text}'
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result and result[0] and result[0][0]:
                return result[0][0][0]
    except:
        pass
    
    # Fallback to original text if translation fails
    return comment_text