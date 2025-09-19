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
        
        # Status translations - fixed "Pass" issue
        'Pass': 'ناجح',
        'PASS': 'ناجح',
        'Passed': 'ناجح',
        'Pass Inspection': 'ناجح',
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
        'Slight oil leak from the engine from below (car needs to be checked)': 'يوجد تهريب زيت بسيط من المحرك من الأسفل (يجب فحص السيارة)',
        'Engine oil needs to be changed': 'زيت المحرك يحتاج إلى تغيير',
        '(no notes provided)': '(لم تُذكر ملاحظات)',
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
    def _fix_common_translation_issues(cls, arabic_text: str) -> str:
        """Fix common Google Translate issues for automotive terms"""
        fixes = {
            'نجح': 'ناجح',  # Fix Pass translation
            'محرك السيارة': 'المحرك',  # Simplify engine
            'فرامل السيارة': 'الفرامل',  # Simplify brakes
            'إطارات السيارة': 'الإطارات',  # Simplify tires
        }
        
        for wrong, correct in fixes.items():
            arabic_text = arabic_text.replace(wrong, correct)
            
        return arabic_text
    
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