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
    # Hardcoded title translations
    title_translations = {
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
    
    if english_text in title_translations:
        return title_translations[english_text]
    
    try:
        import translators as ts
        return ts.translate_text(english_text, translator='bing', from_language='en', to_language='ar')
    except:
        return english_text

def translate_comment_to_arabic(comment_text):
    if not comment_text or not comment_text.strip():
        return ''
    
    # Simple hardcoded translations for testing
    simple_translations = {
        'Front left headlight not working': 'الضوء الأمامي الأيسر لا يعمل',
        'blinker not working': 'الغماز لا يعمل',
        'passenger door scratch': 'خدش باب الراكب',
        'front chassis damaged': 'الشاسيه الأمامي متضرر',
        'rear chassis scratch': 'خدش الشاسيه الخلفي',
        'passenger door repainted': 'باب الراكب معاد طلاؤه',
        'bootlid repainted': 'غطاء الصندوق معاد طلاؤه',
        'engine hood repainted': 'غطاء المحرك معاد طلاؤه',
        'dent on front fender': 'انبعاج في الجناح الأمامي',
        'electrical issues in door': 'مشاكل كهربائية في الباب',
        'belts are loose': 'الأحزمة مفكوكة',
        'needs service': 'يحتاج للصيانة',
        'black smoke from exhaust': 'دخان أسود من العادم'
    }
    
    if comment_text.strip() in simple_translations:
        return simple_translations[comment_text.strip()]
    
    try:
        import translators as ts
        return ts.translate_text(comment_text.strip(), translator='bing', from_language='en', to_language='ar')
    except:
        return comment_text