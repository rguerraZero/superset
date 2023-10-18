"""
Prometheus metric definitions.
"""
import os
from prometheus_client import Counter

_NAME_PREFIX = f'superset_{os.getenv("SUPERSET_ACCESS_METHOD", "internal")}_'
PDF_SUCCESS_COUNTER = Counter(f'{_NAME_PREFIX}pdf_export_success', 'Number of successful pdfs exports')
PDF_FAILURE_COUNTER = Counter(f'{_NAME_PREFIX}pdf_export_failure', 'Number of failures pdfs exports')
