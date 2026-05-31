from collections import Counter
from database import ImportBatch, UploadedFile, ValidationError, Customer

def get_dashboard_stats():
    total_files = UploadedFile.query.count()
    total_batches = ImportBatch.query.count()
    total_success = Customer.query.count()
    total_errors = ValidationError.query.count()
    duplicate_errors = ValidationError.query.filter_by(error_type='duplicate_record').count()
    total_records = sum(batch.total_records for batch in ImportBatch.query.all())
    quality_score = 100 if total_records == 0 else round((total_success / total_records) * 100, 2)
    last_batch = ImportBatch.query.order_by(ImportBatch.created_at.desc()).first()
    return {
        'total_files': total_files,
        'total_batches': total_batches,
        'total_success': total_success,
        'total_errors': total_errors,
        'duplicate_errors': duplicate_errors,
        'quality_score': quality_score,
        'last_import_date': last_batch.created_at.strftime('%Y-%m-%d %H:%M') if last_batch else '-'
    }

def get_error_type_counts():
    counter = Counter(error.error_type for error in ValidationError.query.all())
    return [{'error_type': key, 'count': value} for key, value in counter.most_common()]

def get_file_quality_scores():
    results = []
    batches = ImportBatch.query.order_by(ImportBatch.created_at.desc()).all()
    for batch in batches:
        score = 100 if batch.total_records == 0 else round((batch.clean_records / batch.total_records) * 100, 2)
        results.append({
            'batch_id': batch.id,
            'file_name': batch.uploaded_file.original_filename,
            'total_records': batch.total_records,
            'clean_records': batch.clean_records,
            'error_records': batch.error_records,
            'quality_score': score
        })
    return results
