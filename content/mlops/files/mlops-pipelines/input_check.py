# 2.1 Pipelines and saving models
# Example "input_check" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Check every request before it reaches the model: missing fields, wrong types and impossible values.
SCHEMA = {
    'tenure_months': (float, 0, 600),
    'monthly_bill': (float, 0, 10000),
    'support_calls': (int, 0, 1000),
    'plan': (str, None, None),
}
PLANS = {'basic', 'plus', 'premium'}


def check(request):
    errors = []
    for field, (kind, low, high) in SCHEMA.items():
        if field not in request:
            errors.append(f'{field}: missing')
            continue
        value = request[field]
        if kind is float and isinstance(value, int) and not isinstance(value, bool):
            value = float(value)
        if not isinstance(value, kind) or isinstance(value, bool):
            errors.append(f'{field}: expected {kind.__name__}, got {type(value).__name__}')
            continue
        if low is not None and not low <= value <= high:
            errors.append(f'{field}: {value} is outside {low} to {high}')
    if request.get('plan') not in PLANS and isinstance(request.get('plan'), str):
        errors.append(f"plan: '{request['plan']}' is not one of {sorted(PLANS)} (the model will treat it as unknown)")
    extra = set(request) - set(SCHEMA)
    if extra:
        errors.append(f'unexpected fields: {sorted(extra)}')
    return errors


requests = [
    {'tenure_months': 12, 'monthly_bill': 55.5, 'support_calls': 1, 'plan': 'plus'},
    {'tenure_months': -3, 'monthly_bill': '55', 'support_calls': 1, 'plan': 'plus'},
    {'tenure_months': 12, 'support_calls': 2.5, 'plan': 'student', 'coupon': 'X1'},
]
for r in requests:
    errs = check(r)
    print('OK, send to the model' if not errs else 'Reject with status 422:')
    for e in errs:
        print('   ', e)
