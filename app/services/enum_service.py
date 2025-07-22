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
    
    # Try to find the enum by name
    try:
        # First try direct lookup by name
        return enum_class[input_value]
    except (KeyError, TypeError):
        # Then try to find by value
        for enum_item in enum_class:
            if enum_item.name == input_value or enum_item.value == input_value:
                return enum_item
        
        # If we get here, try the mappings
        if enum_class == Color:
            mapping = COLOR_MAPPING
        elif enum_class == TransmissionType:
            mapping = TRANSMISSION_TYPE_MAPPING
        elif enum_class == FuelType:
            mapping = FUEL_TYPE_MAPPING
        else:
            raise ValueError(f"No mapping available for enum class: {enum_class}")
        
        mapped_value = mapping.get(input_value.upper() if isinstance(input_value, str) else input_value)
        if not mapped_value:
            raise ValueError(f"Invalid value: {input_value}. Expected one of {[e.name for e in enum_class]}.")
        return mapped_value
