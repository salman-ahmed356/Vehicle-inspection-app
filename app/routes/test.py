from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ..database import db
from ..models import Report, ExpertiseReport, ExpertiseFeature

test = Blueprint('test', __name__)

@test.route('/test_form')
def test_form():
    return render_template('test_form.html')

@test.route('/direct_form')
def direct_form():
    return render_template('direct_form.html')

@test.route('/direct_expertise/<int:expertise_report_id>')
def direct_expertise(expertise_report_id):
    from ..models import ExpertiseReport
    
    expertise_report = ExpertiseReport.query.get_or_404(expertise_report_id)
    
    status_choices = [
        'No Issue',
        'Scratch',
        'Dent/Crack/Deformation',
        'Repaired/Painted'
    ]
    
    return render_template(
        'direct_expertise_form.html',
        expertise_report_id=expertise_report_id,
        features=expertise_report.features,
        status_choices=status_choices,
        comment=expertise_report.comment
    )

@test.route('/update_expertise/<int:expertise_report_id>', methods=['POST'])
def update_expertise(expertise_report_id):
    from ..models import ExpertiseReport, ExpertiseFeature
    from ..database import db
    
    expertise_report = ExpertiseReport.query.get_or_404(expertise_report_id)
    
    try:
        # Update features
        for feature in expertise_report.features:
            form_key = f'feature_{feature.id}'
            new_status = request.form.get(form_key)
            print(f"Feature {feature.id} ({feature.name}): current={feature.status}, new={new_status}")
            
            if new_status is not None:
                feature.status = new_status
                db.session.add(feature)
        
        # Update comment
        new_comment = request.form.get('technician_comment') or ''
        if new_comment != expertise_report.comment:
            expertise_report.comment = new_comment
        
        db.session.commit()
        print("Successfully saved all changes")
        return "<h1>Success!</h1><p>Changes saved successfully.</p>"
    
    except Exception as e:
        db.session.rollback()
        print(f"Error updating expertise: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>"

@test.route('/delete_all_reports')
def delete_all_reports():
    try:
        # Get count of reports before deletion
        report_count = Report.query.count()
        
        # Delete all expertise features first
        expertise_reports = ExpertiseReport.query.all()
        for er in expertise_reports:
            # Delete features associated with each expertise report
            ExpertiseFeature.query.filter_by(expertise_report_id=er.id).delete()
        
        # Delete all expertise reports
        ExpertiseReport.query.delete()
        
        # Delete all reports
        Report.query.delete()
        
        # Commit the changes
        db.session.commit()
        
        flash(f"Successfully deleted {report_count} reports and all associated data.", "success")
    except Exception as e:
        flash(f"Error deleting reports: {str(e)}", "error")
    
    return redirect(url_for('main.index'))

@test.route('/test_form_submit', methods=['POST'])
def test_form_submit():
    print("Form submitted!")
    print(f"Form data: {request.form}")
    return jsonify({"success": True})