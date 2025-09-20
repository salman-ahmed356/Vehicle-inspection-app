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
    
    # Arabic to English translations - your common terms
    ARABIC_TO_ENGLISH = {
        # Vehicle info
        'مارسيدس E 2017': 'Mercedes E 2017',
        'ممشاه 163': 'Mileage 163',
        
        # Paint and body work
        'بمبر امامي صبغ': 'Front bumper painted',
        'رفراف امامي يسار صبغ مع معجون': 'Left front fender painted with putty',
        'بمبر أمامي صبغ': 'Front bumper painted',
        'بونيت صبغ مع معجون ويوجد دعمات خفيفة': 'Hood painted with putty and has light supports',
        'باقي القطع صبغ تجميلي': 'Remaining parts cosmetic paint',
        'لايتات تجارية': 'Commercial lights',
        'ماكينة مبطلة': 'Engine disabled',
        'جير مبطل': 'Gearbox disabled',
        'كراسي ماكينة': 'Engine mounts',
        'كراسي جير': 'Gearbox mounts',
        'درامات امامية': 'Front brake drums',
        'جانبينات امامية': 'Front shock absorbers',
        'تواير تحتاج تبديل': 'Tires need replacement',
        'رنجات يوجد بها شحفات': 'Rims have scratches',
        'مقعد السائق الفرش يحتاج تعديل': 'Driver seat upholstery needs adjustment',
        'دبة خلفية مدعومة': 'Rear trunk supported',
        'جانبينات البونيت امامية يجب تغيرهم': 'Front hood shock absorbers need replacement',
        'يوجد ليك بين القير والماكينة': 'There is a leak between gearbox and engine',
        'خدوش في المركبة': 'Scratches on vehicle',
        'خدوش في الرنجات': 'Scratches on rims',
        'صوت خفيف في السوبر يوجد ليك زيت في قطعة واجهة الأمامية': 'Light sound in suspension, oil leak in front part',
        'ليتات امامية تحتاج صيانة': 'Front lights need maintenance',
        'الزجاج الأمامي مكسور': 'Front windshield broken',
        'يوجد نفضه ف المكينه': 'Engine vibration',
        'صدر الأمامي مال المكينه فيها ليك': 'The front chest of the engine has a leak',
        'جانبينات البونيت امامية يجب تغيرهم': 'Front hood shock absorbers need replacement',
        'يوجد ليك بين القير والماكينة': 'There is a leak between gearbox and engine',
        'خدوش في المركبة': 'Scratches on vehicle',
        'خدوش في الرنجات': 'Scratches on rims',
        'صوت خفيف في السوبر يوجد ليك زيت في قطعة واجهة الأمامية': 'Light sound in suspension, oil leak in front part',
        'ليتات امامية تحتاج صيانة': 'Front lights need maintenance',
        'الزجاج الأمامي مكسور': 'Front windshield broken',
        'يوجد نفضه ف المكينه': 'Engine vibration',
        'صدر الأمامي مال المكينه فيها ليك': 'The front chest of the engine has a leak',
        'صبغ باب امامي يمين': 'Right front door painted',
        'صبغ باب خلفي يمين': 'Right rear door painted',
        'رفراف خلفي يسار صبغ': 'Left rear fender painted',
        'نصف رفرفت امامي يسار': 'Half left front fender',
        'يوجد دعمة خفيفة في رفراف امامي يمين مع اللونيت الدعامية امامية': 'Light support in right front fender with front bumper',
        'درامات امامي خلفي': 'Front and rear brake drums',
        'سفايف': 'Brake pads',
        'ليكات مياه': 'Water leaks',
        'ليكات زيت': 'Oil leaks',
        'بوشات امامي وخلفي كامل': 'Complete front and rear bushings',
        'صوت في البيزنغ': 'Sound in bearing',
        'لايت امامي يمين مكسور': 'Right front light broken',
        'ليك في البوكس ستيرنغ مع صوت': 'Leak in steering box with sound',
        'بيرنغات امامي': 'Front bearings',
        'باب امامي يسار صبغ مع معجون': 'Left front door painted with putty',
        'باب أمامي يسار صبغ مع معجون': 'Front left door painted with putty',
        'رفراف أمامي يسار صبغ مع معجون': 'Front left fender painted with putty',
        'باب خلفي يسار صبغ مع معجون': 'Rear left door painted with putty',
        'صبغ من الهيكل داخل مع معجون': 'Interior body painted with putty',
        'دبة خلفية صبغ مع معجون': 'Rear trunk painted with putty',
        'باب خلفي يسار صبغ مع معجون': 'Rear left door painted with putty',
        'باب مخامي يسار': 'Left front door',
        'باب مخامي يسار صبغ مع معجون': 'Left front door painted with putty',
        'باب خلفي يسار صبغ مع معجون': 'Left rear door painted with body filler',
        'صبغ من الهيكل داخل مع معجون': 'Interior body painted with putty',
        'دبة خلفية صبغ مع معجون': 'Rear trunk painted with putty',
        'بونيت صبغ مع معجون ويوجد دعمات خفيفة': 'Hood painted with putty and has light supports',
        'باقي القطع صبغ تجميلي': 'Remaining parts cosmetic paint',
        'صبغ باب امامي يمين': 'Right front door painted',
        'صبغ باب خلفي يمين': 'Right rear door painted',
        'رفراف خلفي يسار صبغ': 'Left rear fender painted',
        'نصف رفرفت امامي يسار': 'Half left front fender',
        'يوجد دعمة خفيفة في رفراف امامي يمين مع اللونيت الدعامية امامية': 'Light support in right front fender with front bumper',
        'دبة خلفية مدعومة': 'Rear trunk supported',
        
        # Mechanical issues
        'لايتات تجارية': 'Commercial lights',
        'ماكينة مبطلة': 'Engine disabled',
        'جير مبطل': 'Gearbox disabled',
        'كراسي ماكينة': 'Engine mounts',
        'كراسي جير': 'Gearbox mounts',
        'درامات امامية': 'Front brake drums',
        'جانبينات امامية': 'Front shock absorbers',
        'تواير تحتاج تبديل': 'Tires need replacement',
        'رنجات يوجد بها شحفات': 'Rims have scratches',
        'مقعد السائق الفرش يحتاج تعديل': 'Driver seat upholstery needs adjustment',
        'جانبينات البونيت امامية يجب تغيرهم': 'Front hood shock absorbers need replacement',
        'يوجد ليك بين القير والماكينة': 'There is a leak between gearbox and engine',
        'خدوش في المركبة': 'Scratches on vehicle',
        'خدوش في الرنجات': 'Scratches on rims',
        'صوت خفيف في السوبر يوجد ليك زيت في قطعة واجهة الأمامية': 'Light sound in suspension, oil leak in front part',
        'ليتات امامية تحتاج صيانة': 'Front lights need maintenance',
        'الزجاج الأمامي مكسور': 'Front windshield broken',
        'يوجد نفضه ف المكينه': 'Engine vibration',
        'صدر الأمامي مال المكينه فيها ليك': 'Front engine cover has leak',
        'درمات امامي خلفي': 'Front and rear brake drums',
        'سفايف': 'Brake pads',
        'ليكات مياه': 'Water leaks',
        'ليكات زيت': 'Oil leaks',
        'بوشات امامي وخلفي كامل': 'Complete front and rear bushings',
        'صوت في البيزنغ': 'Sound in bearing',
        'لايت امامي يمين مكسور': 'Right front light broken',
        'ليك في البوكس ستيرنغ مع صوت': 'Leak in steering box with sound',
        'بيرنغات امامي': 'Front bearings',
        
        # Closing message
        'مع تحيات الفاحص ربيع شركة بلاك بويت نشكركم لحسن تعاونكم معنا نتمنى لكم خدمة افضل': 'With regards from inspector Rabie, Black Point Company. We thank you for your cooperation and wish you better service',
        
        # Fix burning issue
        'يحترقات أمامي': 'Front engine issues',
        'يحترقات امامي': 'Front engine issues',
        'بيرنغات أمامي': 'Front bearings',
        'بيرنغات امامي': 'Front bearings',
        'صدر الأمامي مال المكينه فيها ليك': 'Engine front cover has a leak',
        'يحترقات أمامي': 'Front bearings',
        'بيرنغات امامي': 'Front bearings',
    }
    
    # English to Arabic translations (existing)
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
        """Detect if text is already in Arabic - improved sensitivity"""
        if not text or not text.strip():
            return False
        
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        total_chars = len([c for c in text if c.isalpha()])
        
        # Lower threshold for better Arabic detection
        return arabic_chars > total_chars * 0.2 if total_chars > 0 else False
    
    @classmethod
    def translate_static(cls, text: str) -> str:
        """Translate using static dictionary - USE DICTIONARY FUNCTION FIRST!"""
        if not text or not text.strip():
            return text
        
        # 1. Use the dedicated dictionary translation function FIRST
        from .uae_arabic_dictionary import translate_comment_to_arabic
        
        try:
            translated = translate_comment_to_arabic(text)
            if translated and translated != text and not translated.startswith('ملاحظة:'):
                return translated
        except Exception:
            pass
            
        # 2. Check exact matches in static translations
        if text in cls.STATIC_TRANSLATIONS:
            return cls.STATIC_TRANSLATIONS[text]
            
        # 3. Check automotive phrases
        if text in cls.AUTOMOTIVE_PHRASES:
            return cls.AUTOMOTIVE_PHRASES[text]
            
        # 4. Check case-insensitive in static translations
        text_lower = text.lower()
        for key, value in cls.STATIC_TRANSLATIONS.items():
            if key.lower() == text_lower:
                return value
                
        return text
    
    @classmethod
    def translate_comment(cls, comment: str, source_language: str = None) -> str:
        """Translate comments based on explicit language selection"""
        if not comment or not comment.strip():
            return comment
            
        comment = comment.strip()
        
        # Use explicit language if provided, otherwise auto-detect
        if source_language == 'arabic':
            return cls._translate_arabic_to_english(comment)
        elif source_language == 'english':
            return cls._translate_english_to_arabic(comment)
        else:
            # Fallback to auto-detection for backward compatibility
            if cls.is_arabic(comment):
                return cls._translate_arabic_to_english(comment)
            else:
                return cls._translate_english_to_arabic(comment)
    
    @classmethod
    def _translate_arabic_to_english(cls, arabic_text: str) -> str:
        """Translate Arabic text to English"""
        # Skip translation if text is already English
        if not cls.is_arabic(arabic_text):
            return arabic_text
        
        # Handle multi-line text
        if '\n' in arabic_text:
            lines = arabic_text.split('\n')
            translated_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    translated_line = cls._translate_single_line_arabic(line)
                    translated_lines.append(translated_line)
                else:
                    translated_lines.append('')
            return '\n'.join(translated_lines)
        else:
            return cls._translate_single_line_arabic(arabic_text)
    
    @classmethod
    def _translate_single_line_arabic(cls, arabic_text: str) -> str:
        """Translate single line of Arabic text to English - DICTIONARY FIRST!"""
        # Import the comprehensive dictionary
        from .uae_arabic_dictionary import UAE_ARABIC_TERMS
        
        # 1. Try exact phrase match in comprehensive dictionary FIRST
        # Create reverse lookup from Arabic to English
        arabic_to_english_dict = {v: k for k, v in UAE_ARABIC_TERMS.items()}
        
        if arabic_text in arabic_to_english_dict:
            result = arabic_to_english_dict[arabic_text]
            return result
        
        # 2. Try trimmed version in comprehensive dictionary
        trimmed = arabic_text.strip()
        if trimmed in arabic_to_english_dict:
            result = arabic_to_english_dict[trimmed]
            return result
        
        # 3. Try word-by-word translation using comprehensive dictionary
        words = arabic_text.split()
        translated_words = []
        all_words_translated = True
        
        for word in words:
            word_clean = word.strip('.,!?')
            if word_clean in arabic_to_english_dict:
                translated_words.append(arabic_to_english_dict[word_clean])
            else:
                all_words_translated = False
                break
        
        # Only return word-by-word translation if ALL words were translated
        if all_words_translated and translated_words:
            return ' '.join(translated_words)
        
        # 4. Try exact phrase match in old dictionary
        if arabic_text in cls.ARABIC_TO_ENGLISH:
            result = cls.ARABIC_TO_ENGLISH[arabic_text]
            return result
        
        # 5. Try trimmed version in old dictionary
        if trimmed in cls.ARABIC_TO_ENGLISH:
            result = cls.ARABIC_TO_ENGLISH[trimmed]
            return result
            
        # 6. Fallback: return with English prefix (skip Google Translate for VPS)
        return f"Note: {arabic_text}"
    
    @classmethod
    def _translate_english_to_arabic(cls, english_text: str) -> str:
        """Translate English text to Arabic - USE DICTIONARY FUNCTION FIRST!"""
        # 1. Use the dedicated dictionary translation function FIRST
        from .uae_arabic_dictionary import translate_comment_to_arabic
        
        try:
            translated = translate_comment_to_arabic(english_text)
            if translated and translated != english_text and not translated.startswith('ملاحظة:'):
                return translated
        except Exception:
            pass
        
        # 2. Try exact phrase match in old automotive phrases
        if english_text in cls.AUTOMOTIVE_PHRASES:
            return cls.AUTOMOTIVE_PHRASES[english_text]
            
        # 3. Try case-insensitive phrase match in old automotive phrases
        english_lower = english_text.lower()
        for phrase, translation in cls.AUTOMOTIVE_PHRASES.items():
            if phrase.lower() == english_lower:
                return translation
        
        # 4. Try pattern-based translation for common structures
        translated = cls._pattern_based_translation(english_text)
        if translated != english_text:
            return translated
                
        # 5. Fallback: return with Arabic prefix (skip Google Translate for VPS)
        return f"ملاحظة: {english_text}"
    
    @classmethod
    def _google_translate_with_context(cls, text: str) -> str:
        """Use free Google Translate English to Arabic with UAE automotive context"""
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
    def _google_translate_ar_to_en(cls, arabic_text: str) -> str:
        """Use multiple translation services for better Arabic to English translation"""
        # Skip DeepL as it requires API key and often fails
        # Try Microsoft Translator first
        try:
            import json
            url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from=ar&to=en'
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            data = json.dumps([{'text': arabic_text}])
            response = requests.post(url, data=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0 and 'translations' in result[0]:
                    translated = result[0]['translations'][0]['text']
                    translated = cls._fix_ar_to_en_translation_issues(translated)
                    return translated
        except Exception as e:
            pass
        
        # Fallback to Google Translate with better parameters
        try:
            encoded_text = urllib.parse.quote(arabic_text)
            # Use multiple parameters for better translation quality
            url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl=en&dt=t&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&q={encoded_text}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                result = response.json()
                if result and result[0] and result[0][0]:
                    translated = result[0][0][0]
                    # Clean up common issues
                    translated = translated.replace('Biringat', 'Bearings')
                    translated = translated.replace('biringat', 'bearings')
                    translated = translated.replace('burning', 'bearings')
                    translated = translated.replace('Burning', 'Bearings')
                    translated = translated.replace('chest', 'cover')
                    translated = translated.replace('money', 'part')
                    translated = cls._fix_ar_to_en_translation_issues(translated)
                    return translated
        except Exception as e:
            pass
            
        return arabic_text
    
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
    def _fix_ar_to_en_translation_issues(cls, english_text: str) -> str:
        """Fix common Arabic to English translation issues"""
        fixes = {
            'machine': 'engine',  # ماكينة -> engine not machine
            'gear': 'gearbox',  # جير -> gearbox
            'chairs': 'mounts',  # كراسي -> mounts not chairs
            'drums': 'brake drums',  # درامات -> brake drums
            'sides': 'shock absorbers',  # جانبينات -> shock absorbers
            'tires': 'tires',  # تواير -> tires
            'rims': 'rims',  # رنجات -> rims
            'scratches': 'scratches',  # شحفات -> scratches
            'lights': 'lights',  # لايتات -> lights
            'leak': 'leak',  # ليك -> leak
            'sound': 'noise',  # صوت -> noise
            'bearing': 'bearing',  # بيزنغ -> bearing
            'burning': 'bearings',  # Common mistranslation
            'Burning': 'Bearings',
            'biringat': 'bearings',
            'Biringat': 'Bearings',
            'chest': 'cover',  # صدر -> cover not chest
            'money': 'part',  # مال -> part not money
            'front chest': 'front cover',
            'the money of the engine': 'the engine part',
        }
        
        for wrong, correct in fixes.items():
            english_text = english_text.replace(wrong, correct)
            
        return english_text.strip()
    
    @classmethod
    def get_all_translations_for_template(cls, expertise_reports: list) -> Dict[str, Any]:
        """Get all translations needed for PDF template"""
        translations = {
            'sections': {},
            'features': {},
            'statuses': {},
            'comments': {},
            'comments_english': {}  # New: English translations of Arabic comments
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
            
            # Handle comments bidirectionally
            comment = report.get('comment', '')
            if comment:
                if cls.is_arabic(comment):
                    # Arabic comment -> translate to English
                    translations['comments'][comment] = comment  # Keep original Arabic
                    translations['comments_english'][comment] = cls._translate_arabic_to_english(comment)
                else:
                    # English comment -> translate to Arabic
                    translations['comments'][comment] = cls._translate_english_to_arabic(comment)
                    translations['comments_english'][comment] = comment  # Keep original English
                
        return translations