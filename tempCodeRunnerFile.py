# ==============================================================================
#  THE DEFINITIVE FIX FOR 'ModuleNotFoundError'
#  This block gives Python a "map" to find the 'portal' folder. This is
#  essential for the 'flask' command to work correctly.
# ==============================================================================
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# ==============================================================================

# THE DEFINITIVE FIX FOR LINTER WARNINGS:
# The '# noqa: E402' comment is a standard way to tell your code editor that
# the import below is intentionally placed here and should not be flagged as a warning.
from portal import create_app, db # noqa: E402
from portal.models import User, Material, Assignment, Submission, Announcement, Badge # noqa: E402
from werkzeug.security import generate_password_hash # noqa: E402
from datetime import datetime, timedelta # noqa: E402


# Create the main Flask app instance from our factory
app = create_app()

# --- Database Seeding Logic (Refactored for clarity) ---

def clear_data():
    """Deletes all data from the tables in reverse order of creation."""
    with app.app_context():
        db.session.query(Badge).delete()
        db.session.query(Submission).delete()
        db.session.query(Assignment).delete()
        db.session.query(Material).delete()
        db.session.query(Announcement).delete()
        db.session.query(User).delete()
        db.session.commit()

def create_users():
    """Creates sample users and returns their IDs."""
    with app.app_context():
        admin = User(name="Admin User", email="admin@campus.com", password_hash=generate_password_hash("admin123", method='pbkdf2:sha256'), role="admin")
        faculty = User(name="Dr. Alan Turing", email="faculty@campus.com", password_hash=generate_password_hash("faculty123", method='pbkdf2:sha256'), role="faculty")
        student = User(name="Ada Lovelace", email="student@campus.com", password_hash=generate_password_hash("student123", method='pbkdf2:sha256'), role="student")
        db.session.add_all([admin, faculty, student])
        db.session.commit()
        return admin.id, faculty.id, student.id

def create_announcements(admin_id, faculty_id):
    """Creates sample announcements using user IDs."""
    with app.app_context():
        db.session.add_all([
            Announcement(message="Welcome to Smart Campus Pro! This is the enhanced, fully-functional version.", user_id=admin_id),
            Announcement(message="Mid-term exam schedules have been posted on the main university website.", user_id=faculty_id)
        ])
        db.session.commit()

def create_materials_and_files(faculty_id):
    """Creates materials in the database and creates the physical dummy files."""
    with app.app_context():
        db.session.add_all([
            Material(title="Introduction to Python", description="A comprehensive PDF guide to Python basics.", file_path="dummy_intro_python.pdf", user_id=faculty_id),
            Material(title="Advanced SQL Techniques", description="Presentation slides on complex SQL queries.", file_path="dummy_advanced_sql.pptx", user_id=faculty_id)
        ])
        db.session.commit()
        upload_folder = app.config['UPLOAD_FOLDER']
        open(os.path.join(upload_folder, "dummy_intro_python.pdf"), 'a').close()
        open(os.path.join(upload_folder, "dummy_advanced_sql.pptx"), 'a').close()

def create_assignments(faculty_id):
    """Creates sample assignments and returns the ID of the first one."""
    with app.app_context():
        assignment1 = Assignment(title="Python Programming Basics", description="Write a script to solve 5 basic programming problems.", deadline=datetime.utcnow() + timedelta(days=7), user_id=faculty_id)
        db.session.add_all([
            assignment1,
            Assignment(title="Database Design Document", description="Create an ERD for a library management system.", deadline=datetime.utcnow() + timedelta(days=14), user_id=faculty_id),
            Assignment(title="Past Due Assignment", description="This was due yesterday.", deadline=datetime.utcnow() - timedelta(days=1), user_id=faculty_id)
        ])
        db.session.commit()
        return assignment1.id

def create_submission_and_badge(student_id, assignment_id):
    """Creates a sample submission and awards a badge using IDs."""
    with app.app_context():
        submission = Submission(assignment_id=assignment_id, user_id=student_id, file_path="dummy_submission_ada.zip", status="on-time")
        badge = Badge(user_id=student_id, badge_name="On-Time Submitter")
        db.session.add_all([submission, badge])
        db.session.commit()


@app.cli.command("seed-db")
def seed_db():
    """A Flask CLI command to clear and seed the database with sample data."""
    print("Seeding database...")
    clear_data()
    admin_id, faculty_id, student_id = create_users()
    create_announcements(admin_id, faculty_id)
    create_materials_and_files(faculty_id)
    assignment1_id = create_assignments(faculty_id)
    create_submission_and_badge(student_id, assignment1_id)
    print("Database seeded successfully!")


if __name__ == '__main__':
    # This block allows the app to be run directly with 'python run.py'
    app.run(debug=True)