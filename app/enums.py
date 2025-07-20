from enum import Enum


class TransmissionType(Enum):
    MANUAL = "Manual"
    AUTOMATIC = "Automatic"
    SEMI_AUTOMATIC = "Semi-automatic"


class FuelType(Enum):
    GASOLINE = "Gasoline"
    LPG = "LPG"
    DIESEL = "Diesel"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"


class Color(Enum):
    BEIGE = "Beige"
    WHITE = "White"
    BURGUNDY = "Burgundy"
    SMOKE = "Smoke"
    GRAY = "Gray"
    SILVER_GRAY = "Silver Gray"
    BROWN = "Brown"
    RED = "Red"
    NAVY_BLUE = "Navy Blue"
    BLUE = "Blue"
    PURPLE = "Purple"
    PINK = "Pink"
    YELLOW = "Yellow"
    BLACK = "Black"
    CHAMPAGNE = "Champagne"
    TURQUOISE = "Turquoise"
    ORANGE = "Orange"
    GREEN = "Green"


class ReportStatus(Enum):
    OPENED = "Opened"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class ExpertiseTypeEnum(Enum):
    BOYA = "Paint Expertise"
    KAPORTA = "Body Expertise"
    MOTOR = "Engine Expertise"
    YANAL_KAYMA = "Lateral Drift Expertise"
    SUSPANSIYON = "Suspension Expertise"
    FRENI = "Brake Expertise"
    YOL = "Road Expertise"
    DYNO = "Dyno Expertise"
    BEYIN = "ECU Expertise"
    IC = "Interior Expertise"
    DIS = "Exterior Expertise"
    MEKANIK = "Mechanical Expertise"


class ExpertiseAnswer:
    class IntStatus(Enum):
        ZERO = 0

    class ExpertiseStatus(Enum):
        NO_ISSUE = "No Issue"
        PASSED = "Passed"
        MAY_CAUSE_ISSUES = "May Cause Issues"
        NEEDS_MAINTENANCE = "Needs Maintenance"

    class PaintStatus(Enum):
        ORIGINAL = "Original"
        PLASTIC = "Plastic"
        PAINTED = "Painted"
        LOCALLY_PAINTED = "Locally Painted"
        REPLACED = "Replaced"
        COATED = "Coated"
        NONE = "None"

    class ExtraConditions(Enum):
        REMOVED_REPLACED = "Removed / Replaced"
        DENTLESS = "Dentless"
        DENTED_SCRATCHED = "Dented / Scratched"
        VARNISH = "Varnish"

    class BodyworkStatus(Enum):
        NO_ISSUE = "No Issue"
        SCRATCHED = "Scratched"
        DENTED = "Dented / Broken / Dent"
        PAINTED = "Painted / Worked"

    class OBDStatus(Enum):
        NO_ERROR = "No Error Logged"
        ERROR_LOGGED = "Error Logged"
        NO_CONNECTION = "No Connection"
