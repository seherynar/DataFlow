from database import db, AuditLog

def create_audit_log(action_type, description, file_name=None, batch_id=None):
    log = AuditLog(action_type=action_type, description=description, file_name=file_name, batch_id=batch_id)
    db.session.add(log)
    db.session.commit()
    return log
