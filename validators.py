import re
from datetime import datetime

REQUIRED_CUSTOMER_COLUMNS = ['customer_id','name','email','phone','signup_date','total_spent']

def clean_value(value):
    if value is None:
        return ''
    text = str(value).strip()
    if text.lower() in ['nan','none','nat']:
        return ''
    return text

def validate_required_columns(columns):
    errors = []
    for column in REQUIRED_CUSTOMER_COLUMNS:
        if column not in columns:
            errors.append({
                'row_number': 1,
                'field_name': column,
                'error_type': 'missing_column',
                'message': f'Zorunlu kolon eksik: {column}',
                'original_value': ''
            })
    return errors

def validate_customer_record(row, row_number):
    errors = []

    for field in REQUIRED_CUSTOMER_COLUMNS:
        value = clean_value(row.get(field, ''))
        if value == '':
            errors.append({
                'row_number': row_number,
                'field_name': field,
                'error_type': 'empty_field',
                'message': f'Satır {row_number}: {field} alanı boş olamaz.',
                'original_value': value
            })

    email = clean_value(row.get('email', ''))
    if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        errors.append({
            'row_number': row_number,
            'field_name': 'email',
            'error_type': 'invalid_email',
            'message': f'Satır {row_number}: E-posta formatı hatalı.',
            'original_value': email
        })

    phone = clean_value(row.get('phone', ''))
    digits = re.sub(r'\D', '', phone)
    if phone and len(digits) < 10:
        errors.append({
            'row_number': row_number,
            'field_name': 'phone',
            'error_type': 'invalid_phone',
            'message': f'Satır {row_number}: Telefon formatı hatalı.',
            'original_value': phone
        })

    signup_date = clean_value(row.get('signup_date', ''))
    if signup_date:
        try:
            datetime.strptime(signup_date, '%Y-%m-%d')
        except ValueError:
            errors.append({
                'row_number': row_number,
                'field_name': 'signup_date',
                'error_type': 'invalid_date',
                'message': f'Satır {row_number}: Tarih formatı YYYY-MM-DD olmalıdır.',
                'original_value': signup_date
            })

    total_spent = clean_value(row.get('total_spent', ''))
    if total_spent:
        try:
            number = float(total_spent)
            if number < 0:
                errors.append({
                    'row_number': row_number,
                    'field_name': 'total_spent',
                    'error_type': 'negative_value',
                    'message': f'Satır {row_number}: Toplam harcama negatif olamaz.',
                    'original_value': total_spent
                })
        except ValueError:
            errors.append({
                'row_number': row_number,
                'field_name': 'total_spent',
                'error_type': 'not_numeric',
                'message': f'Satır {row_number}: Toplam harcama sayısal olmalıdır.',
                'original_value': total_spent
            })

    return errors

def detect_duplicate_customers(df):
    errors = []
    if 'customer_id' not in df.columns:
        return errors
    duplicated = df['customer_id'].duplicated(keep=False)
    for index, row in df[duplicated].iterrows():
        errors.append({
            'row_number': int(index) + 2,
            'field_name': 'customer_id',
            'error_type': 'duplicate_record',
            'message': f'Satır {int(index) + 2}: Aynı müşteri kaydı tekrar ediyor.',
            'original_value': clean_value(row.get('customer_id', ''))
        })
    return errors
