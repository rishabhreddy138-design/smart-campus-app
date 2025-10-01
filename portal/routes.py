# pyright: reportMissingImports=false
# import csv
# import io
# import os
# from flask import (Blueprint, render_template, url_for, flash, redirect, request, jsonify, send_from_directory, current_app, Response)
# from flask_login import login_user, current_user, logout_user, login_required
# from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy import func
# from datetime import datetime

# # No more sys.path hacks needed!
# from . import db
# from .models import User, Material, Assignment, Submission, Announcement, Badge
# from .forms import (RegistrationForm, LoginForm, MaterialUploadForm, AssignmentCreationForm, SubmissionForm)
# from .utils import save_file

# # THE DEFINITIVE FIX: The blueprint now correctly finds its templates and static files.
# main_bp = Blueprint('routes', __name__, static_folder='static', template_folder='templates')

# @main_bp.route("/", methods=['GET', 'POST'])
# @main_bp.route("/login", methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('routes.dashboard'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and check_password_hash(user.password_hash, form.password.data):
#             login_user(user, remember=True)
#             return redirect(url_for('routes.dashboard'))
#         else:
#             flash('Login Unsuccessful. Please check email and password.', 'danger')
#     return render_template('login.html', title='Login', form=form)

# @main_bp.route("/register", methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('routes.dashboard'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
#         user = User(name=form.name.data, email=form.email.data, password_hash=hashed_password, role=form.role.data)
#         db.session.add(user)
#         db.session.commit()
#         flash(f'Account created for {form.name.data}! You can now log in.', 'success')
#         return redirect(url_for('routes.login'))
#     return render_template('register.html', title='Register', form=form)

# # ... (The rest of this file is IDENTICAL to the last correct version. You are only changing the first few lines.)
# @main_bp.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('routes.login'))

# def get_student_dashboard_data():
#     submitted_ids = [s.assignment_id for s in current_user.submissions]
#     pending_assignments = Assignment.query.filter(Assignment.id.notin_(submitted_ids), Assignment.deadline > datetime.utcnow()).order_by(Assignment.deadline.asc()).all()
#     total_assignments = db.session.query(Assignment).count()
#     progress = (len(submitted_ids) / total_assignments) * 100 if total_assignments > 0 else 0
#     return {"pending_assignments": pending_assignments, "progress": progress, "badges": current_user.badges}

# def get_faculty_dashboard_data():
#     students = User.query.filter_by(role='student').order_by(User.name).all()
#     assignments = Assignment.query.all()
#     submissions = Submission.query.all()
#     now = datetime.utcnow()
#     submission_map = {(s.user_id, s.assignment_id): s for s in submissions}
#     student_data = []
#     for student in students:
#         status, late_found = 'ok', False
#         for assignment in assignments:
#             submission = submission_map.get((student.id, assignment.id))
#             if submission:
#                 if submission.status == 'late': late_found = True
#             elif assignment.deadline < now:
#                 status = 'missing'; break
#         if status != 'missing' and late_found: status = 'late'
#         student_data.append({'student': student, 'status': status})
#     return {"student_data": student_data}

# @main_bp.route("/dashboard")
# @login_required
# def dashboard():
#     if current_user.role == 'student':
#         announcements = Announcement.query.order_by(Announcement.date_posted.desc()).limit(5).all()
#         return render_template('student_dashboard.html', announcements=announcements, now=datetime.utcnow(), **get_student_dashboard_data())
#     elif current_user.role == 'faculty':
#         return render_template('faculty_dashboard.html', **get_faculty_dashboard_data())
#     else:
#         announcements = Announcement.query.order_by(Announcement.date_posted.desc()).limit(5).all()
#         return render_template('admin_dashboard.html', announcements=announcements, user_count=User.query.count())

# @main_bp.route("/analytics/student/<int:student_id>")
# @login_required
# def student_analytics(student_id):
#     if current_user.role != 'faculty': return jsonify({'error': 'Permission denied'}), 403
#     student = User.query.get_or_404(student_id)
#     total_assignments = db.session.query(Assignment).count()
#     submissions = Submission.query.filter_by(user_id=student_id).all()
#     submitted_count = len(submissions)
#     on_time_count = len([s for s in submissions if s.status == 'on-time'])
#     late_count = submitted_count - on_time_count
#     progress = (submitted_count / total_assignments) * 100 if total_assignments > 0 else 0
#     data = {'name': student.name, 'progress': round(progress), 'submitted_count': submitted_count, 'on_time_count': on_time_count, 'late_count': late_count, 'total_assignments': total_assignments}
#     return render_template('_student_analytics_pane.html', data=data)

# @main_bp.route("/export/assignments")
# @login_required
# def export_assignments():
#     if current_user.role != 'faculty': return redirect(url_for('routes.dashboard'))
#     output, writer = io.StringIO(), csv.writer(output)
#     writer.writerow(['Student Name', 'Assignment Title', 'Status', 'Submission Date'])
#     students, assignments, submissions = User.query.filter_by(role='student').all(), Assignment.query.all(), Submission.query.all()
#     submission_map = {(s.user_id, s.assignment_id): s for s in submissions}
#     for student in students:
#         for assignment in assignments:
#             submission = submission_map.get((student.id, assignment.id))
#             status, date = ("Pending", "N/A")
#             if submission: status, date = (submission.status.title(), submission.submitted_on.strftime('%Y-%m-%d %H:%M'))
#             elif assignment.deadline < datetime.utcnow(): status = "Missing"
#             writer.writerow([student.name, assignment.title, status, date])
#     output.seek(0)
#     return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=submission_report.csv"})

# @main_bp.route("/materials")
# @login_required
# def materials():
#     form = MaterialUploadForm()
#     all_materials = Material.query.order_by(Material.upload_date.desc()).all()
#     return render_template('materials.html', materials=all_materials, form=form)

# @main_bp.route("/materials/upload", methods=['POST'])
# @login_required
# def upload_material():
#     if current_user.role != 'faculty': flash('You do not have permission.', 'danger'); return redirect(url_for('routes.materials'))
#     form = MaterialUploadForm()
#     if form.validate_on_submit():
#         file_path = save_file(form.file.data)
#         db.session.add(Material(title=form.title.data, description=form.description.data, file_path=file_path, uploader=current_user))
#         db.session.commit()
#         flash('Material uploaded successfully!', 'success')
#     else:
#         for error in form.file.errors: flash(f"Upload failed: {error}", 'danger')
#     return redirect(url_for('routes.materials'))

# @main_bp.route('/uploads/<path:filename>')
# @login_required
# def download_file(filename):
#     safe_filename = os.path.basename(filename)
#     return send_from_directory(current_app.config['UPLOAD_FOLDER'], safe_filename, as_attachment=True)

# @main_bp.route("/assignments")
# @login_required
# def assignments():
#     form = AssignmentCreationForm()
#     all_assignments = Assignment.query.order_by(Assignment.deadline.desc()).all()
#     submitted_ids = [s.assignment_id for s in current_user.submissions] if current_user.role == 'student' else []
#     return render_template('assignments.html', assignments=all_assignments, form=form, submitted_ids=submitted_ids, now=datetime.utcnow())

# @main_bp.route("/assignments/create", methods=['POST'])
# @login_required
# def create_assignment():
#     if current_user.role != 'faculty': flash('You do not have permission.', 'danger'); return redirect(url_for('routes.assignments'))
#     form = AssignmentCreationForm()
#     if form.validate_on_submit():
#         file_path = save_file(form.attachment.data) if form.attachment.data else None
#         db.session.add(Assignment(title=form.title.data, description=form.description.data, deadline=form.deadline.data, attachment_path=file_path, creator=current_user))
#         db.session.commit()
#         flash('Assignment created successfully!', 'success')
#     else:
#         flash('Assignment creation failed.', 'danger')
#     return redirect(url_for('routes.assignments'))

# @main_bp.route("/assignment/<int:assignment_id>/submit", methods=['GET', 'POST'])
# @login_required
# def submit_assignment(assignment_id):
#     assignment = Assignment.query.get_or_404(assignment_id)
#     if current_user.role != 'student': flash('Only students can submit.', 'danger'); return redirect(url_for('routes.assignments'))
#     if Submission.query.filter_by(user_id=current_user.id, assignment_id=assignment_id).first():
#         flash('You have already submitted.', 'info'); return redirect(url_for('routes.assignments'))
#     form = SubmissionForm()
#     if form.validate_on_submit():
#         file_path, status = (save_file(form.file.data) if form.file.data else None), ('on-time' if datetime.utcnow() <= assignment.deadline else 'late')
#         db.session.add(Submission(assignment_id=assignment.id, user_id=current_user.id, file_path=file_path, text_content=form.text_content.data, status=status))
#         if status == 'on-time' and not Badge.query.filter_by(user_id=current_user.id, badge_name="On-Time Submitter").first():
#              db.session.add(Badge(user_id=current_user.id, badge_name="On-Time Submitter"))
#         db.session.commit()
#         flash(f'Assignment submitted! Status: {status.upper()}', 'success')
#         return redirect(url_for('routes.assignments'))
#     return render_template('submit_assignment.html', title='Submit Assignment', form=form, assignment=assignment)

# @main_bp.route("/assignment/<int:assignment_id>/submissions")
# @login_required
# def view_submissions(assignment_id):
#     if current_user.role != 'faculty': flash('You do not have permission.', 'danger'); return redirect(url_for('routes.dashboard'))
#     assignment = Assignment.query.get_or_404(assignment_id)
#     return render_template('submissions.html', assignment=assignment, submissions=assignment.submissions.all())

# @main_bp.route("/settings/theme", methods=['POST'])
# @login_required
# def set_theme():
#     theme = request.json.get('theme')
#     if theme in ['light', 'dark']:
#         current_user.theme = theme
#         db.session.commit()
#         return jsonify({'status': 'success'})
#     return jsonify({'status': 'error', 'message': 'Invalid theme'}), 400


# No more sys.path hacks needed in this file! It's now clean.
import csv
import io
import os
from datetime import datetime
from flask import (Blueprint, Response, current_app, flash, jsonify,
                   redirect, render_template, request, send_from_directory,
                   url_for)
from flask_login import (current_user, login_required, login_user,
                         logout_user)  # type: ignore
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .forms import (AssignmentCreationForm, LoginForm, MaterialUploadForm,
                    RegistrationForm, SubmissionForm, ProfileUpdateForm,
                    AnnouncementForm)
from .models import (Announcement, Assignment, Badge, Material, Submission,
                     User, Profile)
from .utils import save_file, save_avatar

main_bp = Blueprint('routes', __name__,
                    template_folder='templates',
                    static_folder='static') # Correctly defined for the blueprint

@main_bp.route("/", methods=['GET', 'POST'])
@main_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if user.is_blocked:
                flash('Your account has been blocked. Contact admin.', 'danger')
                return redirect(url_for('routes.login'))
            login_user(user, remember=True)
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@main_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(name=form.name.data, email=form.email.data, password_hash=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.name.data}! You can now log in.', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Register', form=form)

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

def get_student_dashboard_data():
    """Helper function to fetch data for the student dashboard."""
    submitted_ids = [s.assignment_id for s in current_user.submissions]
    # Pending = all assignments not yet submitted by this student (including past-due)
    query = Assignment.query
    if submitted_ids:
        query = query.filter(~Assignment.id.in_(submitted_ids))
    pending_assignments = query.order_by(Assignment.deadline.asc()).all()
    total_assignments = db.session.query(Assignment).count()
    progress = (len(submitted_ids) / total_assignments) * 100 if total_assignments > 0 else 0
    return {"pending_assignments": pending_assignments, "progress": progress, "badges": current_user.badges, "submitted_ids": submitted_ids}

def get_faculty_dashboard_data():
    """Helper function to fetch and process data for the faculty dashboard."""
    students = User.query.filter_by(role='student').order_by(User.name).all()
    assignments = Assignment.query.all()
    submissions = Submission.query.all()
    now = datetime.utcnow()
    submission_map = {(s.user_id, s.assignment_id): s for s in submissions}

    student_data = []
    for student in students:
        status, late_found = 'ok', False
        for assignment in assignments:
            submission = submission_map.get((student.id, assignment.id))
            if submission:
                if submission.status == 'late': late_found = True
            elif assignment.deadline < now:
                status = 'missing'; break
        if status != 'missing' and late_found: status = 'late'
        student_data.append({'student': student, 'status': status})
    return {"student_data": student_data}

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Renders the correct dashboard based on the user's role."""
    if current_user.role == 'student':
        announcements = Announcement.query.order_by(Announcement.date_posted.desc()).limit(5).all()
        return render_template('student_dashboard.html', announcements=announcements, now=datetime.utcnow(), **get_student_dashboard_data())
    elif current_user.role == 'faculty':
        return render_template('faculty_dashboard.html', **get_faculty_dashboard_data())
    else: # Admin
        announcements = Announcement.query.order_by(Announcement.date_posted.desc()).limit(5).all()
        form = AnnouncementForm()
        return render_template('admin_dashboard.html', announcements=announcements, user_count=User.query.count(), form=form)

@main_bp.route('/announcements/create', methods=['POST'])
@login_required
def create_announcement():
    """Allow only admins to create announcements."""
    if current_user.role != 'admin':
        flash('You do not have permission to create announcements.', 'danger')
        return redirect(url_for('routes.dashboard'))
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(message=form.message.data, user_id=current_user.id)
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement posted.', 'success')
    else:
        for field, errors in form.errors.items():
            for err in errors:
                flash(f"{field}: {err}", 'danger')
    return redirect(url_for('routes.dashboard'))

@main_bp.route('/announcements/<int:announcement_id>/delete', methods=['POST'])
@login_required
def delete_announcement(announcement_id):
    """Allow only admins to delete announcements."""
    if current_user.role != 'admin':
        flash('You do not have permission to delete announcements.', 'danger')
        return redirect(url_for('routes.dashboard'))
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    flash('Announcement deleted.', 'success')
    return redirect(url_for('routes.dashboard'))

@main_bp.route('/admin/overview.json')
@login_required
def admin_overview_json():
    """Return a summarized JSON snapshot of the app for admins."""
    if current_user.role != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    data = {
        'counts': {
            'users': db.session.query(User).count(),
            'materials': db.session.query(Material).count(),
            'assignments': db.session.query(Assignment).count(),
            'submissions': db.session.query(Submission).count(),
            'announcements': db.session.query(Announcement).count(),
            'badges': db.session.query(Badge).count(),
        },
        'latest': {
            'users': [
                {'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role}
                for u in User.query.order_by(User.id.desc()).limit(5).all()
            ],
            'announcements': [
                {'id': a.id, 'message': a.message, 'date_posted': a.date_posted.isoformat(), 'user_id': a.user_id}
                for a in Announcement.query.order_by(Announcement.date_posted.desc()).limit(5).all()
            ],
            'assignments': [
                {'id': asg.id, 'title': asg.title, 'deadline': asg.deadline.isoformat(), 'creator_id': asg.user_id}
                for asg in Assignment.query.order_by(Assignment.created_date.desc()).limit(5).all()
            ],
            'materials': [
                {'id': m.id, 'title': m.title, 'uploaded': m.upload_date.isoformat(), 'uploader_id': m.user_id}
                for m in Material.query.order_by(Material.upload_date.desc()).limit(5).all()
            ],
            'submissions': [
                {'id': s.id, 'assignment_id': s.assignment_id, 'user_id': s.user_id, 'status': s.status, 'submitted_on': s.submitted_on.isoformat()}
                for s in Submission.query.order_by(Submission.submitted_on.desc()).limit(5).all()
            ],
        }
    }
    return jsonify(data)

@main_bp.route("/analytics/student/<int:student_id>")
@login_required
def student_analytics(student_id):
    """Provides detailed analytics for a single student."""
    if current_user.role != 'faculty': return jsonify({'error': 'Permission denied'}), 403
    student = User.query.get_or_404(student_id)
    total_assignments = db.session.query(Assignment).count()
    submissions = Submission.query.filter_by(user_id=student_id).all()
    submitted_count = len(submissions)
    on_time_count = len([s for s in submissions if s.status == 'on-time'])
    late_count = submitted_count - on_time_count
    progress = (submitted_count / total_assignments) * 100 if total_assignments > 0 else 0
    data = {'name': student.name, 'progress': round(progress), 'submitted_count': submitted_count, 'on_time_count': on_time_count, 'late_count': late_count, 'total_assignments': total_assignments}
    return render_template('_student_analytics_pane.html', data=data)

@main_bp.route("/export/assignments")
@login_required
def export_assignments():
    """Generates and serves a CSV report of all student submissions."""
    if current_user.role != 'faculty': return redirect(url_for('routes.dashboard'))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student Name', 'Assignment Title', 'Status', 'Submission Date'])
    students = User.query.filter_by(role='student').all()
    assignments = Assignment.query.all()
    submissions = Submission.query.all()
    submission_map = {(s.user_id, s.assignment_id): s for s in submissions}
    for student in students:
        for assignment in assignments:
            submission = submission_map.get((student.id, assignment.id))
            status, date = ("Pending", "N/A")
            if submission:
                status, date = (submission.status.title(), submission.submitted_on.strftime('%Y-%m-%d %H:%M'))
            elif assignment.deadline < datetime.utcnow():
                status = "Missing"
            writer.writerow([student.name, assignment.title, status, date])
    output.seek(0)
    csv_data = output.getvalue()
    return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=submission_report.csv"})

@main_bp.route("/materials")
@login_required
def materials():
    """Displays all study materials and a form for faculty to upload new ones."""
    form = MaterialUploadForm()
    all_materials = Material.query.order_by(Material.upload_date.desc()).all()
    return render_template('materials.html', materials=all_materials, form=form)

@main_bp.route("/materials/upload", methods=['POST'])
@login_required
def upload_material():
    """Handles the file upload logic for new study materials."""
    if current_user.role != 'faculty':
        flash('You do not have permission.', 'danger')
        return redirect(url_for('routes.materials'))
    form = MaterialUploadForm()
    if form.validate_on_submit():
        file_path = save_file(form.file.data)
        db.session.add(Material(title=form.title.data, description=form.description.data, file_path=file_path, uploader=current_user))
        db.session.commit()
        flash('Material uploaded successfully!', 'success')
    else:
        for error in form.file.errors:
            flash(f"Upload failed: {error}", 'danger')
    return redirect(url_for('routes.materials'))

@main_bp.route("/materials/<int:material_id>/delete", methods=['POST'])
@login_required
def delete_material(material_id):
    """Allows the uploader (faculty) to delete a material and its file."""
    material = Material.query.get_or_404(material_id)
    if not (current_user.role == 'admin' or (current_user.role == 'faculty' and material.user_id == current_user.id)):
        flash('You do not have permission to delete this material.', 'danger')
        return redirect(url_for('routes.materials'))
    try:
        if material.file_path:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(material.file_path))
            if os.path.exists(file_path):
                os.remove(file_path)
    except Exception:
        pass
    db.session.delete(material)
    db.session.commit()
    flash('Material deleted successfully.', 'success')
    return redirect(url_for('routes.materials'))

@main_bp.route('/uploads/<path:filename>')
@login_required
def download_file(filename):
    """Serves files from the upload folder for download."""
    safe_filename = os.path.basename(filename)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], safe_filename, as_attachment=True)

@main_bp.route("/assignments")
@login_required
def assignments():
    """Displays all assignments."""
    form = AssignmentCreationForm()
    all_assignments = Assignment.query.order_by(Assignment.deadline.desc()).all()
    submitted_ids = [s.assignment_id for s in current_user.submissions] if current_user.role == 'student' else []
    # Map of assignment_id -> submission for the current student (to expose their file/text for download/view)
    student_submissions_map = {}
    if current_user.role == 'student':
        subs = Submission.query.filter_by(user_id=current_user.id).all()
        student_submissions_map = {s.assignment_id: s for s in subs}
    return render_template(
        'assignments.html',
        assignments=all_assignments,
        form=form,
        submitted_ids=submitted_ids,
        student_submissions_map=student_submissions_map,
        now=datetime.utcnow()
    )

@main_bp.route("/assignments/create", methods=['POST'])
@login_required
def create_assignment():
    """Handles the logic for faculty to create a new assignment."""
    if current_user.role != 'faculty':
        flash('You do not have permission.', 'danger')
        return redirect(url_for('routes.assignments'))
    form = AssignmentCreationForm()
    if form.validate_on_submit():
        file_path = save_file(form.attachment.data) if form.attachment.data else None
        db.session.add(Assignment(title=form.title.data, description=form.description.data, deadline=form.deadline.data, attachment_path=file_path, creator=current_user))
        db.session.commit()
        flash('Assignment created successfully!', 'success')
    else:
        flash('Assignment creation failed. Please check the form.', 'danger')
    return redirect(url_for('routes.assignments'))

@main_bp.route("/assignments/<int:assignment_id>/delete", methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    """Allows the creator (faculty) to delete an assignment, its attachment, and submissions."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if not (current_user.role == 'admin' or (current_user.role == 'faculty' and assignment.user_id == current_user.id)):
        flash('You do not have permission to delete this assignment.', 'danger')
        return redirect(url_for('routes.assignments'))
    try:
        if assignment.attachment_path:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(assignment.attachment_path))
            if os.path.exists(file_path):
                os.remove(file_path)
    except Exception:
        pass
    submissions = assignment.submissions.all()
    for submission in submissions:
        try:
            if submission.file_path:
                sub_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(submission.file_path))
                if os.path.exists(sub_path):
                    os.remove(sub_path)
        except Exception:
            pass
        db.session.delete(submission)
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment and related submissions deleted.', 'success')
    return redirect(url_for('routes.assignments'))

@main_bp.route("/assignment/<int:assignment_id>/submit", methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    """Displays the submission page for an assignment and handles the submission."""
    assignment = Assignment.query.get_or_404(assignment_id)
    if current_user.role != 'student':
        flash('Only students can submit.', 'danger')
        return redirect(url_for('routes.assignments'))
    if Submission.query.filter_by(user_id=current_user.id, assignment_id=assignment_id).first():
        flash('You have already submitted.', 'info')
        return redirect(url_for('routes.assignments'))
    form = SubmissionForm()
    if form.validate_on_submit():
        file_path = save_file(form.file.data) if form.file.data else None
        status = 'on-time' if datetime.utcnow() <= assignment.deadline else 'late'
        submission = Submission(assignment_id=assignment.id, user_id=current_user.id, file_path=file_path, text_content=form.text_content.data, status=status)
        db.session.add(submission)
        if status == 'on-time' and not Badge.query.filter_by(user_id=current_user.id, badge_name="On-Time Submitter").first():
             db.session.add(Badge(user_id=current_user.id, badge_name="On-Time Submitter"))
        db.session.commit()
        flash(f'Assignment submitted! Status: {status.upper()}', 'success')
        return redirect(url_for('routes.assignments'))
    elif request.method == 'POST':
        # Surface validation errors to the user
        for field, errors in form.errors.items():
            for err in errors:
                flash(f"{field}: {err}", 'danger')
    return render_template('submit_assignment.html', title='Submit Assignment', form=form, assignment=assignment)

@main_bp.route("/assignment/<int:assignment_id>/submissions")
@login_required
def view_submissions(assignment_id):
    """Allows faculty to view all submissions for a specific assignment."""
    if current_user.role != 'faculty':
        flash('You do not have permission.', 'danger')
        return redirect(url_for('routes.dashboard'))
    assignment = Assignment.query.get_or_404(assignment_id)
    return render_template('submissions.html', assignment=assignment, submissions=assignment.submissions.all())

@main_bp.route("/settings/theme", methods=['POST'])
@login_required
def set_theme():
    """Saves the user's theme preference to the database."""
    theme = request.json.get('theme')
    if theme in ['light', 'dark']:
        current_user.theme = theme
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid theme'}), 400

@main_bp.route('/admin/users')
@login_required
def admin_users():
    """List all users for admins with their roles."""
    if current_user.role != 'admin':
        flash('Permission denied.', 'danger')
        return redirect(url_for('routes.dashboard'))
    users = User.query.order_by(User.name.asc()).all()
    return render_template('admin_users.html', users=users)

@main_bp.route('/admin/users/<int:user_id>/block', methods=['POST'])
@login_required
def block_user(user_id):
    """Admin can block a user (prevents login)."""
    if current_user.role != 'admin':
        flash('Permission denied.', 'danger')
        return redirect(url_for('routes.dashboard'))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot block yourself.', 'warning')
        return redirect(url_for('routes.admin_users'))
    user.is_blocked = True
    db.session.commit()
    flash(f'Blocked {user.name}.', 'success')
    return redirect(url_for('routes.admin_users'))

@main_bp.route('/admin/users/<int:user_id>/unblock', methods=['POST'])
@login_required
def unblock_user(user_id):
    """Admin can unblock a user."""
    if current_user.role != 'admin':
        flash('Permission denied.', 'danger')
        return redirect(url_for('routes.dashboard'))
    user = User.query.get_or_404(user_id)
    user.is_blocked = False
    db.session.commit()
    flash(f'Unblocked {user.name}.', 'success')
    return redirect(url_for('routes.admin_users'))

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update the current user's profile, including avatar."""
    user = current_user
    if not user.profile:
        user.profile = Profile(user_id=user.id)
        db.session.add(user.profile)
        db.session.commit()
    form = ProfileUpdateForm()
    if form.validate_on_submit():
        if form.name.data:
            user.name = form.name.data
        if form.department.data:
            user.profile.department = form.department.data
        user.profile.bio = form.bio.data
        if form.avatar.data:
            try:
                # delete old avatar if any
                if user.profile.avatar_path:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(user.profile.avatar_path))
                    if os.path.exists(old_path):
                        os.remove(old_path)
            except Exception:
                pass
            user.profile.avatar_path = save_avatar(form.avatar.data)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('routes.profile'))
    # Pre-fill form
    form.name.data = user.name
    form.department.data = user.profile.department
    form.bio.data = user.profile.bio
    return render_template('profile.html', form=form, user=user)