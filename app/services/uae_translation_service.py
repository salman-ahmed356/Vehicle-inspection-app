"""
UAE Translation Service - Single Source of Truth
Handles all Arabic translations for vehicle inspection reports
"""
import re
import requests
import urllib.parse
from typing import Optional, Dict, Any


class UaeTranslationService:
    """Unified translation service for UAE Arabic automotive terms"""
    
    # Static translations - 100% accurate UAE automotive terms
    STATIC_TRANSLATIONS = {
        # Section headers - your corrected translations
        'Additional to Body': 'إضافات إلى الهيكل',
        'LIGHTS': 'المصابيح',
        'BODY': 'الهيكل', 
        'CHASSIS': 'الشاسيه',
        'ROOF': 'السقف',
        'BONNET AND TRUNK': 'غطاء المحرك والصندوق',
        'FENDERS': 'الرفارف',
        'DOORS': 'الأبواب',
        'BUMPER AND KIT': 'الصدامات والكيت',
        'ENGINE': 'المحرك',
        'GEAR BOX': 'الجير بوكس',
        'PAINT': 'الصبغ',
        'RIMS': 'الرنجات',
        'DIFFERENTIAL': 'الدفرنشن',
        '4W DRIVE (4X4)': 'الفور ويل (الرباعي)',
        'TRANSMISSION SHAFT': 'عامود ناقل الحركة',
        'ALIGNMENT': 'الميزانيه',
        'TYRES': 'الإطارات',
        'BRAKES': 'الفرامل',
        'EXHAUST': 'الأكزوز',
        
        # Status translations - fixed "Pass" issue
        'Pass': 'ناجح',
        'PASS': 'ناجح',
        'Passed': 'ناجح',
        'Pass Inspection': 'ناجح',
        'pass': 'ناجح',
        'No Issue': 'لا يوجد مشكلة',
        'No ISSUE': 'لا يوجد مشكلة',
        'Original': 'أصلي',
        'Painted': 'مطلي',
        'Repainted': 'تم إعادة طلائه',
        'Damaged': 'متضرر',
        'Good': 'جيد',
        'OK': 'جيد',
        
        # Vehicle parts
        'Headlights': 'المصابيح الأمامية',
        'Front Bumper': 'الصدام الأمامي',
        'Rear Bumper': 'الصدام الخلفي',
        'Left Front Fender': 'الرفرف الأمامي الأيسر',
        'Right Front Fender': 'الرفرف الأمامي الأيمن',
        'Left Rear Fender': 'الرفرف الخلفي الأيسر',
        'Right Rear Fender': 'الرفرف الخلفي الأيمن',
        'Left Front Door': 'الباب الأمامي الأيسر',
        'Right Front Door': 'الباب الأمامي الأيمن',
        'Left Rear Door': 'الباب الخلفي الأيسر',
        'Right Rear Door': 'الباب الخلفي الأيمن',
        
        # Expertise types
        'Paint Expertise': 'خبرة الطلاء',
        'Body Expertise': 'خبرة الهيكل',
        'Paint & Body Expertise': 'خبرة الطلاء والهيكل',
        'Engine Expertise': 'خبرة المحرك',
        'Brake Expertise': 'خبرة الفرامل',
        'Suspension Expertise': 'خبرة نظام التعليق',
        'Interior Expertise': 'خبرة الداخلية',
        'Exterior Expertise': 'خبرة الخارجية',
        'Mechanical Expertise': 'خبرة الميكانيكية',
        'ECU Expertise': 'خبرة وحدة التحكم الإلكترونية',
    }
    
    # Common automotive phrases - your corrected translations
    AUTOMOTIVE_PHRASES = {
        'Headlights need polish': 'المصابيح الأمامية تحتاج إلى تلميع',
        'Windshield water pump motor not working': 'مضخة مياه الزجاج الأمامي لا تعمل',
        'Chassis is rusty from below': 'يوجد صدأ في الشاسيه من الأسفل',
        'Part of chassis is not good': 'جزء من الشاسيه غير جيد',
        'Front left fender repainted': 'الرفرف الأمامي الأيسر تم إعادة طلائه',
        'Front right fender repainted': 'الرفرف الأمامي الأيمن تم إعادة طلائه',
        'Front left door repainted': 'الباب الأمامي الأيسر تم إعادة طلائه',
        'Front right door repainted': 'الباب الأمامي الأيمن تم إعادة طلائه',
        'Rear left door repainted': 'الباب الخلفي الأيسر تم إعادة طلائه',
        'Rear right door repainted': 'الباب الخلفي الأيمن تم إعادة طلائه',
        'Front bumper repainted': 'الصدام الأمامي تم إعادة طلائه',
        'Front bumper has a slight dent': 'غطاء المحرك الأمامي به انبعاج طفيف',
        'Slight oil leak from the engine from below (car needs to be checked)': 'يوجد تهريب زيت بسيط من المحرك من الأسفل (يجب فحص السيارة)',
        'Slight oil leak from the engine from below (car needs to be washed to check oil leak)': 'يوجد تهريب زيت بسيط من المحرك من الأسفل (يجب فحص السيارة)',
        'Engine/gearbox mounts need to be changed': 'يجب تبديل قواعد المحرك بسبب تلف أو كسر فيها',
        'Engine oil needs to be changed': 'زيت المحرك يحتاج إلى تغيير',
        '(no notes provided)': '(لم تُذكر ملاحظات)',
        
        # Common automotive patterns
        'oil leak': 'تهريب زيت',
        'needs to be changed': 'يحتاج إلى تغيير',
        'needs to be checked': 'يجب فحصه',
        'repainted': 'تم إعادة طلائه',
        'slight dent': 'انبعاج طفيف',
        'from below': 'من الأسفل',
        'car needs': 'السيارة تحتاج',
        'engine mount': 'قواعد المحرك',
        'gearbox mount': 'قواعد الجير',
    }
    
    @classmethod
    def is_arabic(cls, text: str) -> bool:
        """Detect if text is already in Arabic"""
        if not text or not text.strip():
            return False
        
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        total_chars = len([c for c in text if c.isalpha()])
        
        return arabic_chars > total_chars * 0.3 if total_chars > 0 else False
    
    @classmethod
    def translate_static(cls, text: str) -> str:
        """Translate using static dictionary - instant and accurate"""
        if not text or not text.strip():
            return text
            
        # Check exact matches first
        if text in cls.STATIC_TRANSLATIONS:
            return cls.STATIC_TRANSLATIONS[text]
            
        # Check automotive phrases
        if text in cls.AUTOMOTIVE_PHRASES:
            return cls.AUTOMOTIVE_PHRASES[text]
            
        # Check case-insensitive
        text_lower = text.lower()
        for key, value in cls.STATIC_TRANSLATIONS.items():
            if key.lower() == text_lower:
                return value
                
        return text
    
    @classmethod
    def translate_comment(cls, comment: str) -> str:
        """Translate free-form comments using hybrid approach"""
        if not comment or not comment.strip():
            return comment
            
        comment = comment.strip()
        
        # If already Arabic, return as-is
        if cls.is_arabic(comment):
            return comment
            
        # Try exact phrase match first
        if comment in cls.AUTOMOTIVE_PHRASES:
            return cls.AUTOMOTIVE_PHRASES[comment]
            
        # Try case-insensitive phrase match
        comment_lower = comment.lower()
        for phrase, translation in cls.AUTOMOTIVE_PHRASES.items():
            if phrase.lower() == comment_lower:
                return translation
        
        # Try pattern-based translation for common structures
        translated = cls._pattern_based_translation(comment)
        if translated != comment:
            return translated
                
        # Try Google Translate with UAE automotive context
        try:
            return cls._google_translate_with_context(comment)
        except Exception:
            # Fallback: return with Arabic prefix
            return f"ملاحظة: {comment}"
    
    @classmethod
    def _google_translate_with_context(cls, text: str) -> str:
        """Use free Google Translate with UAE automotive context"""
        try:
            # Add UAE automotive context
            enhanced_text = f"UAE vehicle inspection: {text}"
            encoded_text = urllib.parse.quote(enhanced_text)
            
            url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={encoded_text}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result and result[0] and result[0][0]:
                    translated = result[0][0][0]
                    # Clean up the translation
                    translated = translated.replace('فحص المركبة الإماراتية:', '').strip()
                    translated = translated.replace('UAE vehicle inspection:', '').strip()
                    
                    # Apply common fixes
                    translated = cls._fix_common_translation_issues(translated)
                    
                    return translated
                    
        except Exception:
            pass
            
        return text
    
    @classmethod
    def _pattern_based_translation(cls, text: str) -> str:
        """Translate using common automotive patterns"""
        import re
        
        # Pattern: "X needs to be Y"
        pattern1 = re.compile(r'(.+?)\s+needs?\s+to\s+be\s+(.+)', re.IGNORECASE)
        match1 = pattern1.match(text)
        if match1:
            part = match1.group(1).strip()
            action = match1.group(2).strip()
            part_ar = cls.translate_static(part)
            if 'changed' in action.lower():
                return f'{part_ar} يحتاج إلى تغيير'
            elif 'checked' in action.lower():
                return f'{part_ar} يجب فحصه'
            elif 'repaired' in action.lower():
                return f'{part_ar} يحتاج إلى إصلاح'
        
        # Pattern: "X has Y"
        pattern2 = re.compile(r'(.+?)\s+has?\s+(.+)', re.IGNORECASE)
        match2 = pattern2.match(text)
        if match2:
            part = match2.group(1).strip()
            issue = match2.group(2).strip()
            part_ar = cls.translate_static(part)
            if 'dent' in issue.lower():
                return f'{part_ar} به انبعاج'
            elif 'leak' in issue.lower():
                return f'{part_ar} به تهريب'
        
        # Pattern: "X is Y"
        pattern3 = re.compile(r'(.+?)\s+is\s+(.+)', re.IGNORECASE)
        match3 = pattern3.match(text)
        if match3:
            part = match3.group(1).strip()
            condition = match3.group(2).strip()
            part_ar = cls.translate_static(part)
            if 'rusty' in condition.lower():
                return f'{part_ar} به صدأ'
            elif 'damaged' in condition.lower():
                return f'{part_ar} متضرر'
            elif 'not good' in condition.lower():
                return f'{part_ar} غير جيد'
        
        return text
    
    @classmethod
    def _fix_common_translation_issues(cls, arabic_text: str) -> str:
        """Fix common Google Translate issues for automotive terms"""
        fixes = {
            'نجح': 'ناجح',  # Fix Pass translation
            'محرك السيارة': 'المحرك',  # Simplify engine
            'فرامل السيارة': 'الفرامل',  # Simplify brakes
            'إطارات السيارة': 'الإطارات',  # Simplify tires
            'يحتاج إلى أن يتم غسله': 'يجب فحصه',  # Fix washing to checking
            'للتحقق من': 'لفحص',  # Simplify checking
            'فحص المركبة الإماراتية': '',  # Remove UAE context prefix
        }
        
        for wrong, correct in fixes.items():
            arabic_text = arabic_text.replace(wrong, correct)
            
        return arabic_text.strip()
    
    @classmethod
    def get_all_translations_for_template(cls, expertise_reports: list) -> Dict[str, Any]:
        """Get all translations needed for PDF template"""
        translations = {
            'sections': {},
            'features': {},
            'statuses': {},
            'comments': {}
        }
        
        for report in expertise_reports:
            # Translate section names
            section_name = report.get('expertise_type_name', '')
            if section_name:
                translations['sections'][section_name] = cls.translate_static(section_name)
            
            # Translate features and statuses
            for feature in report.get('features', []):
                feature_name = feature.get('name', '')
                feature_status = feature.get('status', '')
                
                if feature_name:
                    translations['features'][feature_name] = cls.translate_static(feature_name)
                if feature_status:
                    translations['statuses'][feature_status] = cls.translate_static(feature_status)
            
            # Translate comments
            comment = report.get('comment', '')
            if comment:
                translations['comments'][comment] = cls.translate_comment(comment)
                
        return translations