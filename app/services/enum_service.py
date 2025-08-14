from ..enums import TransmissionType, FuelType, Color

COLOR_MAPPING = {
    'BEJ': Color.BEIGE,
    'BEYAZ': Color.WHITE,
    'BORDO': Color.BURGUNDY,
    'FÜME': Color.SMOKE,
    'GRİ': Color.GRAY,
    'GÜMÜŞ GRİ': Color.SILVER_GRAY,
    'KAHVERENGİ': Color.BROWN,
    'KIRMIZI': Color.RED,
    'LACİVERT': Color.NAVY_BLUE,
    'MAVİ': Color.BLUE,
    'MOR': Color.PURPLE,
    'PEMBE': Color.PINK,
    'SARI': Color.YELLOW,
    'SİYAH': Color.BLACK,
    'ŞAMPANYA': Color.CHAMPAGNE,
    'TURKUAZ': Color.TURQUOISE,
    'TURUNCU': Color.ORANGE,
    'YEŞİL': Color.GREEN,
}

TRANSMISSION_TYPE_MAPPING = {
    'DÜZ VİTES': TransmissionType.MANUAL,
    'OTOMATİK': TransmissionType.AUTOMATIC,
    'YARI OTOMATİK': TransmissionType.SEMI_AUTOMATIC,
}

FUEL_TYPE_MAPPING = {
    'BENZİN': FuelType.GASOLINE,
    'BENZİN + LPG': FuelType.LPG,
    'DİZEL': FuelType.DIESEL,
    'ELEKTRİKLİ': FuelType.ELECTRIC,
    'HİBRİT': FuelType.HYBRID,
}


def map_to_enum(input_value, enum_class):
    """
    Convert a string enum name to the actual enum value.
    
    Args:
        input_value: The string name of the enum (e.g., 'MANUAL' or 'Manual')
        enum_class: The enum class (e.g., TransmissionType)
        
    Returns:
        The enum value
    """
    # If it's already an enum instance, return it
    if isinstance(input_value, enum_class):
        return input_value
    
    # If input is None or empty, return the first enum value as default
    if not input_value:
        return list(enum_class)[0]
    
    # Try to find the enum by name (case insensitive)
    try:
        # First try direct lookup by name
        return enum_class[input_value.upper()]
    except (KeyError, TypeError, AttributeError):
        pass
    
    # Try to find by value or name (case insensitive)
    try:
        for enum_item in enum_class:
            if (enum_item.name.upper() == str(input_value).upper() or 
                enum_item.value.upper() == str(input_value).upper()):
                return enum_item
    except (AttributeError, TypeError):
        pass
    
    # Try the mappings as fallback
    try:
        if enum_class == Color:
            mapping = COLOR_MAPPING
        elif enum_class == TransmissionType:
            mapping = TRANSMISSION_TYPE_MAPPING
        elif enum_class == FuelType:
            mapping = FUEL_TYPE_MAPPING
        else:
            # Return first enum value as default
            return list(enum_class)[0]
        
        mapped_value = mapping.get(str(input_value).upper())
        if mapped_value:
            return mapped_value
    except (AttributeError, TypeError):
        pass
    
    # Final fallback - return first enum value
    return list(enum_class)[0]