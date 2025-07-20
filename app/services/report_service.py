import json
from datetime import datetime

from ..database import db
from ..models import (
    Report,
    Customer,
    VehicleOwner,
    Vehicle,
    Agent,
    Address,
    Staff,
    PackageExpertise,
    ExpertiseReport,
    ExpertiseType,
    ExpertiseFeature
)


def load_expertise_map(file_path='data/expertise_map.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading expertise map: {e}")
        return {}


def get_default_features_for_expertise_type(expertise_name, expertise_map=None):
    if expertise_map is None:
        expertise_map = load_expertise_map()
    return expertise_map.get(expertise_name, [])


def create_report(
    inspection_date,
    vehicle_id,
    customer_id,
    package_id,
    operation,
    created_by,
    registration_document_seen
):
    # Avoid duplicates
    existing = Report.query.filter_by(
        vehicle_id=vehicle_id,
        customer_id=customer_id,
        package_id=package_id
    ).first()
    if existing:
        return existing

    # 1) Create the Report
    report = Report(
        inspection_date=inspection_date,
        vehicle_id=vehicle_id,
        customer_id=customer_id,
        package_id=package_id,
        operation=operation,
        created_by=created_by,
        registration_document_seen=registration_document_seen
    )
    db.session.add(report)
    db.session.commit()  # now report.id and report relationship are usable

    # 2) For each PackageExpertise, seed an ExpertiseReport + default features
    pkg_experts = PackageExpertise.query.filter_by(package_id=package_id).all()
    for pe in pkg_experts:
        # create ExpertiseReport without report_id kwarg
        er = ExpertiseReport(
            expertise_type_id=pe.expertise_type_id,
            comment=""
        )
        db.session.add(er)
        db.session.flush()         # assigns er.id
        er.report = report         # set the relationship AFTER flush

        # grab the defaults from JSON map
        et = ExpertiseType.query.get(pe.expertise_type_id)
        defaults = get_default_features_for_expertise_type(et.name)
        for part in defaults:
            feature = ExpertiseFeature(
                expertise_report_id=er.id,
                name=part['part_name'],
                status=part['default_status']
            )
            db.session.add(feature)

    db.session.commit()
    return report


def get_or_create_customer(form_data):
    full = form_data.get('customer_name', '') or ''
    first, _, last = full.partition(' ')

    customer = Customer.query.filter_by(
        first_name=first,
        last_name=last,
        phone_number=form_data.get('customer_phone'),
        tc_tax_number=form_data.get('customer_tax_no'),
        email=form_data.get('customer_email')
    ).first()

    if not customer:
        customer = Customer(
            first_name=first,
            last_name=last,
            phone_number=form_data.get('customer_phone') or '',
            tc_tax_number=form_data.get('customer_tax_no') or '',
            email=form_data.get('customer_email') or ''
        )
        db.session.add(customer)
        db.session.commit()

        address_str = form_data.get('customer_address') or ''
        if address_str:
            addr = Address(
                street_address=address_str,
                city=form_data.get('customer_city', '') or '',
                state=form_data.get('customer_state', '') or '',
                postal_code=form_data.get('customer_postal_code', '') or ''
            )
            db.session.add(addr)
            db.session.commit()

            customer.address = addr
            db.session.commit()

    return customer


def get_or_create_vehicle_owner(form_data):
    full = form_data.get('owner_name', '') or ''
    first, _, last = full.partition(' ')

    owner = VehicleOwner.query.join(Address).filter(
        VehicleOwner.first_name == first,
        VehicleOwner.last_name == last,
        VehicleOwner.tc_tax_number == form_data.get('owner_tax_no'),
        VehicleOwner.phone_number == form_data.get('owner_phone'),
        Address.street_address == form_data.get('owner_address', '')
    ).first()

    if not owner:
        addr = Address(
            street_address=form_data.get('owner_address') or '',
            city=form_data.get('owner_city', '') or '',
            state=form_data.get('owner_state', '') or '',
            postal_code=form_data.get('owner_postal_code', '') or ''
        )
        db.session.add(addr)
        db.session.commit()

        owner = VehicleOwner(
            first_name=first,
            last_name=last,
            tc_tax_number=form_data.get('owner_tax_no') or '',
            phone_number=form_data.get('owner_phone') or ''
        )
        owner.address = addr
        db.session.add(owner)
        db.session.commit()

    return owner


def get_or_create_agent(agent_name, report_id):
    first, _, last = agent_name.partition(' ')
    agent = Agent.query.filter_by(
        first_name=first,
        last_name=last
    ).first()

    if not agent:
        agent = Agent(
            first_name=first,
            last_name=last,
            report_id=report_id
        )
        db.session.add(agent)
    else:
        agent.report_id = report_id
        db.session.add(agent)

    # do not commit here; caller will commit
    return agent


def get_or_create_staff_by_name(staff_name):
    first, _, last = staff_name.partition(' ')
    staff = Staff.query.filter_by(
        first_name=first,
        last_name=last
    ).first()

    if not staff:
        staff = Staff(first_name=first, last_name=last)
        db.session.add(staff)
        db.session.commit()

    return staff


def get_or_create_vehicle(form_data):
    vehicle = Vehicle.query.filter_by(
        plate=form_data['vehicle_plate'],
        chassis_number=form_data['chassis_number']
    ).first()

    if not vehicle:
        vehicle = Vehicle(
            plate=form_data['vehicle_plate'],
            engine_number=form_data['engine_number'],
            brand=form_data['brand'],
            model=form_data['model'],
            chassis_number=form_data['chassis_number'],
            color=form_data['color'],
            model_year=int(form_data['model_year']),
            transmission_type=form_data['gear_type'],
            fuel_type=form_data['fuel_type'],
            mileage=int(form_data['vehicle_km'])
        )
        db.session.add(vehicle)
        db.session.commit()

    return vehicle
