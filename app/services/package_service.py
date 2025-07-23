from ..models import Package

def get_active_packages():
    """
    Returns only active packages from the database.
    """
    return Package.query.filter_by(active=True).all()