import os
import json
from datetime import datetime

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename

from database import db, UploadedFile, ImportBatch, RawRecord, ValidationError, AuditLog
from validators import validate_required_columns, validate_customer_record, detect_duplicate_customers
from audit import create_audit_log
from importer import import_clean_customers, rollback_import
from reports import get_dashboard_stats, get_error_type_counts, get_file_quality_scores

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')
DATA_FOLDER = os.path.join(BASE_DIR, 'data')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXPORT_FOLDER'] = EXPORT_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(DATA_FOLDER, 'dataflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

_initialized = False

def ensure_directories():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    os.makedirs(DATA_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv', 'xlsx', 'xls']

def read_uploaded_file(file_path, filename):
    if filename.lower().endswith('.csv'):
        return pd.read_csv(file_path)
    return pd.read_excel(file_path)

def analyze_and_store_file(uploaded_file):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.stored_filename)
    df = read_uploaded_file(file_path, uploaded_file.stored_filename)
    df = df.where(pd.notnull(df), '')

    all_errors = []
    all_errors.extend(validate_required_columns(df.columns))
    all_errors.extend(detect_duplicate_customers(df))

    for index, row in df.iterrows():
        row_number = int(index) + 2
        all_errors.extend(validate_customer_record(row, row_number))

    error_rows = {error['row_number'] for error in all_errors if error['row_number'] != 1}
    clean_records = max(len(df) - len(error_rows), 0)

    batch = ImportBatch(
        uploaded_file_id=uploaded_file.id,
        total_records=len(df),
        clean_records=clean_records,
        error_records=len(error_rows),
        duplicate_records=sum(1 for error in all_errors if error['error_type'] == 'duplicate_record')
    )
    db.session.add(batch)
    db.session.commit()

    has_column_error = any(error['error_type'] == 'missing_column' for error in all_errors)

    for index, row in df.iterrows():
        row_number = int(index) + 2
        raw_record = RawRecord(
            batch_id=batch.id,
            row_number=row_number,
            data_json=json.dumps(row.to_dict(), ensure_ascii=False),
            is_clean=(row_number not in error_rows and not has_column_error)
        )
        db.session.add(raw_record)

    for error in all_errors:
        validation_error = ValidationError(
            batch_id=batch.id,
            row_number=error['row_number'],
            field_name=error['field_name'],
            error_type=error['error_type'],
            message=error['message'],
            original_value=str(error.get('original_value', ''))
        )
        db.session.add(validation_error)

    db.session.commit()
    create_audit_log('analyze_file', f'Dosya analiz edildi. Temiz: {clean_records}, hatalı: {len(error_rows)}.', uploaded_file.original_filename, batch.id)
    return batch

@app.before_request
def initialize_database():
    global _initialized
    if not _initialized:
        ensure_directories()
        db.create_all()
        _initialized = True

@app.route('/')
def dashboard():
    return render_template('dashboard.html', stats=get_dashboard_stats(), error_counts=get_error_type_counts(), quality_scores=get_file_quality_scores()[:5])

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('data_file')
        if file is None or file.filename == '':
            return render_template('upload.html', error='Dosya seçilmedi.')
        if not allowed_file(file.filename):
            return render_template('upload.html', error='Sadece CSV veya Excel dosyası yükleyebilirsin.')

        original_filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        stored_filename = f'{timestamp}_{original_filename}'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)
        file.save(file_path)

        uploaded_file = UploadedFile(original_filename=original_filename, stored_filename=stored_filename, file_type=original_filename.rsplit('.', 1)[1].lower())
        db.session.add(uploaded_file)
        db.session.commit()
        create_audit_log('upload_file', 'Dosya sisteme yüklendi.', original_filename, None)
        batch = analyze_and_store_file(uploaded_file)
        return redirect(url_for('preview', batch_id=batch.id))
    return render_template('upload.html')

@app.route('/preview/<int:batch_id>')
def preview(batch_id):
    batch = ImportBatch.query.get_or_404(batch_id)
    raw_records = RawRecord.query.filter_by(batch_id=batch.id).order_by(RawRecord.row_number.asc()).limit(10).all()
    errors = ValidationError.query.filter_by(batch_id=batch.id).order_by(ValidationError.row_number.asc()).all()
    rows = [json.loads(record.data_json) for record in raw_records]
    table_html = pd.DataFrame(rows).to_html(index=False, classes='table table-striped table-bordered') if rows else ''
    return render_template('preview.html', batch=batch, table_html=table_html, errors=errors)

@app.route('/errors/<int:batch_id>')
def errors(batch_id):
    batch = ImportBatch.query.get_or_404(batch_id)
    errors = ValidationError.query.filter_by(batch_id=batch.id).order_by(ValidationError.row_number.asc()).all()
    return render_template('errors.html', batch=batch, errors=errors)

@app.route('/import/<int:batch_id>', methods=['POST'])
def import_batch(batch_id):
    import_clean_customers(batch_id)
    return redirect(url_for('imports'))

@app.route('/rollback/<int:batch_id>', methods=['POST'])
def rollback_batch(batch_id):
    rollback_import(batch_id)
    return redirect(url_for('imports'))

@app.route('/imports')
def imports():
    batches = ImportBatch.query.order_by(ImportBatch.created_at.desc()).all()
    return render_template('imports.html', batches=batches)

@app.route('/audit-logs')
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
    return render_template('audit_logs.html', logs=logs)

@app.route('/reports')
def reports():
    return render_template('reports.html', error_counts=get_error_type_counts(), quality_scores=get_file_quality_scores())

@app.route('/export-errors/<int:batch_id>')
def export_errors(batch_id):
    batch = ImportBatch.query.get_or_404(batch_id)
    errors = ValidationError.query.filter_by(batch_id=batch.id).all()
    rows = [{
        'row_number': error.row_number,
        'field_name': error.field_name,
        'error_type': error.error_type,
        'message': error.message,
        'original_value': error.original_value
    } for error in errors]
    export_path = os.path.join(app.config['EXPORT_FOLDER'], f'errors_batch_{batch.id}.csv')
    pd.DataFrame(rows).to_csv(export_path, index=False, encoding='utf-8-sig')
    create_audit_log('export_errors', 'Hatalı kayıt raporu dışa aktarıldı.', batch.uploaded_file.original_filename, batch.id)
    return send_file(export_path, as_attachment=True)

if __name__ == '__main__':
    ensure_directories()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5050)
