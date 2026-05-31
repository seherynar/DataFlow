from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ImportBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uploaded_file_id = db.Column(db.Integer, db.ForeignKey('uploaded_file.id'), nullable=False)
    total_records = db.Column(db.Integer, default=0)
    clean_records = db.Column(db.Integer, default=0)
    error_records = db.Column(db.Integer, default=0)
    duplicate_records = db.Column(db.Integer, default=0)
    imported_records = db.Column(db.Integer, default=0)
    imported = db.Column(db.Boolean, default=False)
    rolled_back = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    imported_at = db.Column(db.DateTime, nullable=True)
    rolled_back_at = db.Column(db.DateTime, nullable=True)
    uploaded_file = db.relationship('UploadedFile', backref='batches')

class RawRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('import_batch.id'), nullable=False)
    row_number = db.Column(db.Integer, nullable=False)
    data_json = db.Column(db.Text, nullable=False)
    is_clean = db.Column(db.Boolean, default=False)

class ValidationError(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('import_batch.id'), nullable=False)
    row_number = db.Column(db.Integer, nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    error_type = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    original_value = db.Column(db.String(255), nullable=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('import_batch.id'), nullable=False)
    customer_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    signup_date = db.Column(db.String(20), nullable=False)
    total_spent = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=True)
    batch_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
