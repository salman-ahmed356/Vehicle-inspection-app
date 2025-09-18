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
    """
    Get UAE Arabic translation for automotive terms.
    Falls back to Microsoft Translator for unknown terms.
    """
    # Check if it's a known UAE term
    if english_text in UAE_ARABIC_TERMS:
        return UAE_ARABIC_TERMS[english_text]
    
    # For unknown terms, use Microsoft Translator with UAE Arabic
    try:
        import translators as ts
        # Try with region first, fallback without region
        try:
            return ts.translate_text(english_text, translator='bing', from_language='en', to_language='ar', region='AE')
        except:
            return ts.translate_text(english_text, translator='bing', from_language='en', to_language='ar')
    except:
        return english_text  # Return original if translation fails

def translate_comment_to_arabic(comment_text):
    """
    Translate comment text to Arabic, using dictionary for known terms
    and translator for the rest.
    """
    if not comment_text or not comment_text.strip():
        return ''
    
    # First check if the entire comment is a known term
    if comment_text.strip() in UAE_ARABIC_TERMS:
        return UAE_ARABIC_TERMS[comment_text.strip()]
    
    # For longer text, use full translator with UAE Arabic
    try:
        import translators as ts
        # Try with region first, fallback without region
        try:
            return ts.translate_text(comment_text, translator='bing', from_language='en', to_language='ar', region='AE')
        except:
            return ts.translate_text(comment_text, translator='bing', from_language='en', to_language='ar')
    except:
        return comment_text