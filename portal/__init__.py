import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import text

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # THE DEFINITIVE FIX: The static_folder is now correctly inside the portal package.
    # We no longer need any confusing relative paths.
    app = Flask(__name__, instance_relative_config=True)
    
    app.config['SECRET_KEY'] = 'a_very_secret_key_that_is_long_and_secure_and_should_be_changed'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    # The UPLOAD_FOLDER is now correctly placed inside the app's new static directory
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'
    login_manager.login_message_category = 'info'

    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        # Ensure 'is_blocked' column exists on 'user' table (SQLite safe)
        try:
            existing_columns = [row['name'] for row in db.session.execute(text("PRAGMA table_info(user)")).mappings()]
            if 'is_blocked' not in existing_columns:
                db.session.execute(text("ALTER TABLE user ADD COLUMN is_blocked BOOLEAN NOT NULL DEFAULT 0"))
                db.session.commit()
        except Exception:
            # Do not crash app startup if pragma/alter fails; leave DB as-is
            db.session.rollback()

    return app