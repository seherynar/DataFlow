import re
from datetime import datetime

REQUIRED_CUSTOMER_COLUMNS = [
    'customer_id',
    'name',
    'email',
    'phone',
    'signup_date',
    'total_spent'
]


def clean_value(value):
    if value is None:
        return ''

    text = str(value).strip()

    if text.lower() in ['nan', 'none', 'nat']:
        return ''

    return text


def add_error(errors, row_number, field_name, error_type, message, original_value=''):
    errors.append({
        'row_number': row_number,
        'field_name': field_name,
        'error_type': error_type,
        'message': message,
        'original_value': original_value
    })


def validate_required_columns(columns):
    errors = []
    columns = list(columns)

    for column in REQUIRED_CUSTOMER_COLUMNS:
        if column not in columns:
            add_error(
                errors=errors,
                row_number=1,
                field_name=column,
                error_type='missing_column',
                message=f'Zorunlu kolon eksik: {column}',
                original_value=''
            )

    return errors


def validate_customer_record(row, row_number):
    errors = []

    for field in REQUIRED_CUSTOMER_COLUMNS:
        value = clean_value(row.get(field, ''))

        if value == '':
            add_error(
                errors=errors,
                row_number=row_number,
                field_name=field,
                error_type='empty_field',
                message=f'{field} alanı boş olamaz.',
                original_value=value
            )

    email = clean_value(row.get('email', ''))

    if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        add_error(
            errors=errors,
            row_number=row_number,
            field_name='email',
            error_type='invalid_email',
            message='E-posta formatı hatalı.',
            original_value=email
        )

    phone = clean_value(row.get('phone', ''))
    phone_digits = re.sub(r'\D', '', phone)

    if phone and len(phone_digits) < 10:
        add_error(
            errors=errors,
            row_number=row_number,
            field_name='phone',
            error_type='invalid_phone',
            message='Telefon formatı hatalı.',
            original_value=phone
        )

    signup_date = clean_value(row.get('signup_date', ''))

    if signup_date:
        try:
            datetime.strptime(signup_date, '%Y-%m-%d')
        except ValueError:
            add_error(
                errors=errors,
                row_number=row_number,
                field_name='signup_date',
                error_type='invalid_date',
                message='Tarih formatı YYYY-MM-DD olmalıdır.',
                original_value=signup_date
            )

    total_spent = clean_value(row.get('total_spent', ''))

    if total_spent:
        try:
            total_spent_number = float(total_spent)

            if total_spent_number < 0:
                add_error(
                    errors=errors,
                    row_number=row_number,
                    field_name='total_spent',
                    error_type='negative_value',
                    message='Toplam harcama negatif olamaz.',
                    original_value=total_spent
                )

        except ValueError:
            add_error(
                errors=errors,
                row_number=row_number,
                field_name='total_spent',
                error_type='not_numeric',
                message='Toplam harcama sayısal olmalıdır.',
                original_value=total_spent
            )

    return errors


def detect_duplicate_customers(df):
    errors = []

    if 'customer_id' not in df.columns:
        return errors

    customer_ids = df['customer_id'].apply(clean_value)

    duplicated = customer_ids.duplicated(keep=False) & (customer_ids != '')

    for index, row in df[duplicated].iterrows():
        row_number = int(index) + 2
        customer_id = clean_value(row.get('customer_id', ''))

        add_error(
            errors=errors,
            row_number=row_number,
            field_name='customer_id',
            error_type='duplicate_record',
            message='Aynı müşteri kaydı tekrar ediyor.',
            original_value=customer_id
        )

    return errors