from ..database import db
from ..models import Company, Address, Branch, Staff


def get_first_company():
    company = Company.query.first()
    return company


def create_company(data):
    # Create or get the address instance
    address = Address(
        street_address=data.get('street_address'),
        city=data['city'],
        state=data.get('state'),
        postal_code=data.get('postal_code')
    )
    db.session.add(address)
    db.session.flush()  # Ensure address ID is available

    new_company = Company(
        name=data['name'],
        phone=data.get('phone'),
        fax=data.get('fax'),
        email=data.get('email'),
        website=data.get('website'),
        address=address  # Assign the Address instance
    )
    db.session.add(new_company)
    db.session.commit()
    return new_company


def update_company_service(company, data):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Updating company ID: {company.id} with data: {data}")
    
    # Log the data being used to update the company
    logger.info(f"Updating company with data: {data}")
    
    company.name = data['name']
    company.phone = data.get('phone')
    company.fax = data.get('fax')
    company.email = data.get('email')
    company.website = data.get('website')
    # Removed my_business_address_link temporarily
    
    # Log the updated company object
    logger.info(f"Updated company object: {company.name}, {company.phone}, {company.email}")

    # Update or create the address
    if company.address:
        logger.info(f"Updating existing address ID: {company.address.id}")
        company.address.street_address = data.get('street_address')
        company.address.city = data['city']
        company.address.state = data.get('state')
        company.address.postal_code = data.get('postal_code')
        logger.info(f"Updated address: {company.address.street_address}, {company.address.city}, {company.address.state}, {company.address.postal_code}")
    else:
        logger.info("Creating new address for company")
        address = Address(
            street_address=data.get('street_address'),
            city=data['city'],
            state=data.get('state'),
            postal_code=data.get('postal_code')
        )
        db.session.add(address)
        db.session.flush()
        company.address_id = address.id
        logger.info(f"Created new address with ID: {address.id}")

    # Update associated branches and their staff
    branch_count = len(company.branches) if company.branches else 0
    logger.info(f"Company has {branch_count} branches")
    
    # If no branches exist, create one
    if branch_count == 0:
        logger.info("Creating default branch for company")
        branch = Branch(
            name='Main',
            company_id=company.id,
            address_id=company.address_id
        )
        db.session.add(branch)
        db.session.flush()
        logger.info(f"Created branch with ID: {branch.id}")
    else:
        for branch in company.branches:
            staff_count = len(branch.staff_members) if branch.staff_members else 0
            logger.info(f"Branch ID: {branch.id} has {staff_count} staff members")
            
            # If no staff exists, create one
            if staff_count == 0:
                logger.info("Creating default staff for branch")
                from werkzeug.security import generate_password_hash
                default_staff = Staff(
                    first_name="Admin",
                    last_name="User",
                    password=generate_password_hash("password123", method='pbkdf2:sha256', salt_length=16),
                    phone_number=company.phone or "000-000-0000",
                    department="Management",
                    role="Manager",
                    branch_id=branch.id
                )
                db.session.add(default_staff)
                db.session.flush()
                logger.info(f"Created staff with ID: {default_staff.id}")
            else:
                for staff in branch.staff_members:
                    # Update staff details if needed
                    if data.get('contact_name'):
                        staff.first_name = data.get('contact_name')
                    if data.get('contact_phone'):
                        staff.phone_number = data.get('contact_phone')

    try:
        db.session.commit()
        logger.info("Successfully committed company updates")
        return company
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating company: {str(e)}")
        raise


def delete_company(company):
    db.session.delete(company)
    db.session.commit()


def create_default_company():
    first_company = get_first_company()
    if first_company:
        return first_company

    # Create a default address
    default_address = Address(
        street_address="X sokağı Y Mah. Buca İzmir",
        city="İzmir",
        state="",
        postal_code=""
    )
    db.session.add(default_address)
    db.session.flush()  # Ensure address ID is available

    default_company = Company(
        name="Firma Adı",
        phone="000-000-0000",
        fax="000-000-0000",
        email="deneme@company.com",
        website="https://www.defaultcompany.com",
        address=default_address  # Assign the Address instance
    )
    db.session.add(default_company)
    db.session.flush()  # Ensure company ID is available

    # Create a default branch
    default_branch = Branch(
        name="Bayi",
        company_id=default_company.id,
        address_id=default_address.id
    )
    db.session.add(default_branch)
    db.session.flush()  # Ensure branch ID is available

    # Create a default staff member
    default_staff = Staff(
        first_name="Yetkili",
        last_name="Kişi",
        password="defaultpassword",  # Ensure to hash passwords in a real application
        phone_number="000-000-0000",
        department="Default Department",
        role="Manager",
        branch_id=default_branch.id
    )
    db.session.add(default_staff)

    db.session.commit()
    return default_company


