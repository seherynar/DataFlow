import json
from datetime import datetime
from database import db, ImportBatch, RawRecord, Customer
from audit import create_audit_log

def import_clean_customers(batch_id):
    batch = ImportBatch.query.get_or_404(batch_id)
    if batch.imported and not batch.rolled_back:
        return 0

    clean_records = RawRecord.query.filter_by(batch_id=batch.id, is_clean=True).all()
    count = 0
    for raw_record in clean_records:
        data = json.loads(raw_record.data_json)
        customer = Customer(
            batch_id=batch.id,
            customer_id=str(data.get('customer_id', '')).strip(),
            name=str(data.get('name', '')).strip(),
            email=str(data.get('email', '')).strip(),
            phone=str(data.get('phone', '')).strip(),
            signup_date=str(data.get('signup_date', '')).strip(),
            total_spent=float(data.get('total_spent', 0))
        )
        db.session.add(customer)
        count += 1

    batch.imported = True
    batch.rolled_back = False
    batch.imported_records = count
    batch.imported_at = datetime.utcnow()
    db.session.commit()
    create_audit_log('import_clean_records', f'{count} temiz kayıt aktarıldı.', batch.uploaded_file.original_filename, batch.id)
    return count

def rollback_import(batch_id):
    batch = ImportBatch.query.get_or_404(batch_id)
    if not batch.imported or batch.rolled_back:
        return 0

    count = Customer.query.filter_by(batch_id=batch.id).delete()
    batch.rolled_back = True
    batch.rolled_back_at = datetime.utcnow()
    db.session.commit()
    create_audit_log('rollback_import', f'{count} kayıt geri alındı.', batch.uploaded_file.original_filename, batch.id)
    return count
