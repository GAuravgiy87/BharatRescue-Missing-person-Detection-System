from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class MissingPerson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    last_seen_location = db.Column(db.String(200), nullable=False)
    last_seen_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    aadhar_number = db.Column(db.String(12))
    photo_filename = db.Column(db.String(255), nullable=False)
    face_encoding = db.Column(db.LargeBinary)  # Store face encoding as binary data
    status = db.Column(db.String(20), default='missing')  # missing, found, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MissingPerson {self.name}>'

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    missing_person_id = db.Column(db.Integer, db.ForeignKey('missing_person.id'), nullable=False)
    detected_location = db.Column(db.String(200))
    detection_time = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Float)
    notified = db.Column(db.Boolean, default=False)
    
    missing_person = db.relationship('MissingPerson', backref=db.backref('detections', lazy=True))

    def __repr__(self):
        return f'<Detection {self.id} for {self.missing_person.name}>'

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'
