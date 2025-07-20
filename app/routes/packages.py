from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database import db
from app.models import Report, ExpertiseType, PackageExpertise, Package
from app.forms.package_form import PackageForm

packages = Blueprint('packages', __name__, url_prefix='/packages')


@packages.route('/', methods=['GET'])
def packages_list():
    form   = PackageForm()
    packs  = Package.query.all()
    return render_template(
        'packages.html',
        form=form,
        packages=packs,
        update=False
    )


@packages.route('/add', methods=['POST'])
def add_pckg():
    form = PackageForm(request.form)

    if form.validate_on_submit():
        # 1) Create the Package itself
        new_pkg = Package(
            name = form.name.data,
            price = form.price.data,
            active = (form.active.data == 'active')
        )
        db.session.add(new_pkg)
        db.session.commit()  # so new_pkg.id is available

        # 2) Link each selected expertise by name → ExpertiseType.id
        for expertise_name in form.contents.data:
            et = ExpertiseType.query.filter_by(name=expertise_name).first()
            if et:
                link = PackageExpertise(
                    package_id= new_pkg.id,
                    expertise_type_id= et.id
                )
                db.session.add(link)

        db.session.commit()
        flash('Package successfully created!', 'success')
    else:
        flash(f'Please fix the errors: {form.contents.errors}', 'error')

    return redirect(url_for('packages.packages_list'))


@packages.route('/update/<int:package_id>', methods=['GET', 'POST'])
def update_package(package_id):
    pkg  = Package.query.get_or_404(package_id)
    form = PackageForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        # Update basic fields
        pkg.name   = form.name.data
        pkg.price  = form.price.data
        pkg.active = (form.active.data == 'active')
        db.session.commit()

        # Clear old links
        PackageExpertise.query.filter_by(package_id=pkg.id).delete()
        db.session.commit()

        # Re‐add new links
        for expertise_name in form.contents.data:
            et = ExpertiseType.query.filter_by(name=expertise_name).first()
            if et:
                link = PackageExpertise(
                    package_id= pkg.id,
                    expertise_type_id= et.id
                )
                db.session.add(link)
        db.session.commit()

        flash('Package updated!', 'success')
        return redirect(url_for('packages.packages_list'))

    # GET: pre‐populate form
    form.name.data     = pkg.name
    form.price.data    = pkg.price
    form.active.data   = 'active' if pkg.active else 'inactive'
    # pull the linked ExpertiseType names back into the multi‐select
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


@packages.route('/delete/<int:package_id>', methods=['POST'])
def delete_package(package_id):
    pkg = Package.query.get_or_404(package_id)

    if Report.query.filter_by(package_id=package_id).count():
        flash('Cannot delete: package in use', 'error')
    else:
        db.session.delete(pkg)
        db.session.commit()
        flash('Package deleted', 'success')

    return redirect(url_for('packages.packages_list'))
