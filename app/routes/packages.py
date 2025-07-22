# File: app/routes/packages.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database import db
from app.models import Report, ExpertiseType, PackageExpertise, Package
from app.forms.package_form import PackageForm, DEFAULT_EXPERTISE_TYPES

packages = Blueprint('packages', __name__, url_prefix='/packages')


def _populate_contents(form):
    """
    Populate the WTForms SelectMultipleField with all expertise names.
    The form already has default choices, but we'll try to get them from the database.
    """
    form.populate_expertise_choices()


@packages.route('/', methods=['GET'])
def packages_list():
    form = PackageForm()
    _populate_contents(form)
    packs = Package.query.all()
    return render_template(
        'packages.html',
        form=form,
        packages=packs,
        update=False
    )


@packages.route('/add', methods=['POST'])
def add_pckg():
    form = PackageForm(request.form)
    _populate_contents(form)

    if form.validate_on_submit():
        pkg = Package(
            name   = form.name.data,
            price  = form.price.data,
            active = (form.active.data == 'active')
        )
        db.session.add(pkg)
        db.session.commit()

        for name in form.contents.data:
            # Try to find the expertise type in the database
            et = ExpertiseType.query.filter_by(name=name).first()
            
            # If not found, create it
            if not et and name in DEFAULT_EXPERTISE_TYPES:
                et = ExpertiseType(name=name)
                db.session.add(et)
                db.session.commit()
                print(f"Created expertise type: {name}")
            
            # Add the package expertise link
            if et:
                db.session.add(PackageExpertise(
                    package_id        = pkg.id,
                    expertise_type_id = et.id
                ))

        db.session.commit()
        flash('Package successfully created!', 'success')
    else:
        flash(f'Please fix the errors: {form.contents.errors}', 'error')

    return redirect(url_for('packages.packages_list'))


@packages.route('/update/<int:package_id>', methods=['GET', 'POST'])
def update_package(package_id):
    pkg = Package.query.get_or_404(package_id)

    if request.method == 'POST':
        form = PackageForm(request.form)
        _populate_contents(form.contents)

        if form.validate_on_submit():
            pkg.name   = form.name.data
            pkg.price  = form.price.data
            pkg.active = (form.active.data == 'active')
            db.session.commit()

            # clear old links and add new ones
            PackageExpertise.query.filter_by(package_id=pkg.id).delete()
            db.session.commit()
            for name in form.contents.data:
                # Try to find the expertise type in the database
                et = ExpertiseType.query.filter_by(name=name).first()
                
                # If not found, create it
                if not et and name in DEFAULT_EXPERTISE_TYPES:
                    et = ExpertiseType(name=name)
                    db.session.add(et)
                    db.session.commit()
                    print(f"Created expertise type: {name}")
                
                # Add the package expertise link
                if et:
                    db.session.add(PackageExpertise(
                        package_id        = pkg.id,
                        expertise_type_id = et.id
                    ))
            db.session.commit()

            flash('Package updated!', 'success')
            return redirect(url_for('packages.packages_list'))

    else:
        # GET: build form and pre-select existing expertises
        form = PackageForm()
        _populate_contents(form)

        form.name.data   = pkg.name
        form.price.data  = pkg.price
        form.active.data = 'active' if pkg.active else 'inactive'

        linked = PackageExpertise.query.filter_by(package_id=pkg.id).all()
        form.contents.data = [
            ExpertiseType.query.get(pe.expertise_type_id).name
            for pe in linked
        ]

        return render_template(
            'packages.html',
            form=form,
            packages=Package.query.all(),
            update=True,
            current_pkg=pkg
        )

    # if POST validation failed, fall back to list view
    return render_template(
        'packages.html',
        form=form,
        packages=Package.query.all(),
        update=True,
        current_pkg=pkg
    )


@packages.route('/delete/<int:package_id>', methods=['POST'])
def delete_package(package_id):
    pkg = Package.query.get_or_404(package_id)

    # first delete any Reports using this package
    Report.query.filter_by(package_id=package_id).delete()
    db.session.delete(pkg)
    db.session.commit()

    flash('Package and its reports deleted', 'success')
    return redirect(url_for('packages.packages_list'))
