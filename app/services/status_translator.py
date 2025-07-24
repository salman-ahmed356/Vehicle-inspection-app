class StatusTranslator:
    """Translates expertise status values to Arabic"""
    
    # Paint Expertise Status Translations (from boya_expertise.html)
    PAINT_STATUS_AR = {
        "Original": "أصلي",
        "Plastic": "بلاستيك", 
        "Painted": "مطلي",
        "Locally Painted": "مطلي محلياً",
        "Replaced": "مستبدل",
        "Coated": "مطلي بالورنيش",
        "None": "لا يوجد"
    }
    
    # Body Expertise Status Translations (from boya_kaporta_expertise.html)
    BODY_STATUS_AR = {
        "No Issue": "لا توجد مشكلة",
        "Scratch": "خدش",
        "Dent/Crack/Deformation": "مقعر/شق/تشويه",
        "Repaired/Painted": "مصلح/مطلي"
    }
    
    # Engine Expertise Status Translations
    ENGINE_STATUS_AR = {
        "No Issue": "لا توجد مشكلة", 
        "Passed": "نجح",
        "May Cause Issues": "قد يسبب مشاكل",
        "Needs Maintenance": "يحتاج صيانة"
    }
    
    # Lateral Drift, Suspension, Brake Status Translations (numeric values)
    NUMERIC_STATUS_AR = {
        "0": "صفر",
        0: "صفر"
    }
    
    # ECU Expertise Status Translations
    ECU_STATUS_AR = {
        "No Error Logged": "لا توجد أخطاء مسجلة",
        "Error Logged": "خطأ مسجل",
        "No Connection": "لا يوجد اتصال"
    }
    
    # Mechanical Status Translations (from mekanik_expertise.html)
    MECHANICAL_STATUS_AR = {
        "No Issue": "لا توجد مشكلة",
        "Scratch": "خدش",
        "Dent/Crack/Deformation": "مقعر/شق/تشويه",
        "Repaired/Painted": "مصلح/مطلي"
    }
    
    # Interior/Exterior Status Translations
    GENERAL_STATUS_AR = {
        "No Issue": "لا توجد مشكلة",
        "No ISSUE": "لا توجد مشكلة",
        "Passed": "نجح",
        "May Cause Issues": "قد يسبب مشاكل",
        "Needs Maintenance": "يحتاج صيانة"
    }
    
    @classmethod
    def translate_paint_status(cls, english_status):
        """Translate paint expertise status to Arabic"""
        return cls.PAINT_STATUS_AR.get(english_status, english_status)
    
    @classmethod  
    def translate_body_status(cls, english_status):
        """Translate body expertise status to Arabic"""
        return cls.BODY_STATUS_AR.get(english_status, english_status)
        
    @classmethod
    def translate_engine_status(cls, english_status):
        """Translate engine expertise status to Arabic"""
        return cls.ENGINE_STATUS_AR.get(english_status, english_status)
    
    @classmethod
    def translate_numeric_status(cls, status):
        """Translate numeric status to Arabic"""
        return cls.NUMERIC_STATUS_AR.get(status, str(status))
    
    @classmethod
    def translate_ecu_status(cls, english_status):
        """Translate ECU expertise status to Arabic"""
        return cls.ECU_STATUS_AR.get(english_status, english_status)
    
    @classmethod
    def translate_mechanical_status(cls, english_status):
        """Translate mechanical expertise status to Arabic"""
        return cls.MECHANICAL_STATUS_AR.get(english_status, english_status)
    
    @classmethod
    def translate_general_status(cls, english_status):
        """Translate general expertise status to Arabic"""
        return cls.GENERAL_STATUS_AR.get(english_status, english_status)
    
    @classmethod
    def get_translated_status(cls, expertise_type, english_status):
        """Get translated status based on expertise type"""
        if expertise_type == "Paint Expertise":
            return cls.translate_paint_status(english_status)
        elif expertise_type == "Body Expertise":
            return cls.translate_body_status(english_status)
        elif expertise_type == "Engine Expertise":
            return cls.translate_engine_status(english_status)
        elif expertise_type in ["Lateral Drift Expertise", "Suspension Expertise", "Brake Expertise"]:
            return cls.translate_numeric_status(english_status)
        elif expertise_type == "Road Expertise":
            return english_status  # Empty expertise
        elif expertise_type == "Dyno Expertise":
            return cls.translate_numeric_status(english_status)
        elif expertise_type == "ECU Expertise":
            return cls.translate_ecu_status(english_status)
        elif expertise_type == "Mechanical Expertise":
            return cls.translate_mechanical_status(english_status)
        elif expertise_type in ["Interior Expertise", "Exterior Expertise"]:
            return cls.translate_general_status(english_status)
        elif "Paint & Body" in expertise_type:
            # Handle combined Paint & Body expertise - check both paint and body statuses
            if english_status in cls.PAINT_STATUS_AR:
                return cls.translate_paint_status(english_status)
            elif english_status in cls.BODY_STATUS_AR:
                return cls.translate_body_status(english_status)
            else:
                return english_status
        else:
            return english_status