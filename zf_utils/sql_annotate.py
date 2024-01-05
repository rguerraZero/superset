import json

from flask import request, current_app
from sqlalchemy import Table
from typing import Dict, Optional
from urllib.parse import urlparse, parse_qs


def _parse_dashboard_id_from_url(url) -> str:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    dashboard_id = query_params.get('dashboard_id', [None])[0]

    return dashboard_id


def _parse_slice_id_from_url(url) -> str:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    form_data_str = query_params.get('form_data', [None])[0]

    if form_data_str:
        try:
            form_data = json.loads(form_data_str)
            return form_data.get('slice_id')
        except json.JSONDecodeError:
            return None
    return None


def get_context_data_from_sqla(table: Table) -> Dict:
    """
    Get context data from a SQLAlchemy table.

    Args:
        table (Table): The SQLAlchemy table object.

    Returns:
        dict: A dictionary containing the following context data:
            - 'dataset_name': The name of the table.
            - 'dataset_id': The ID of the table.
            - 'db_engine_spec': The database engine specification of the table.
            - 'dashboard_id': The ID of the dashboard parsed from the URL.
            - 'slice_id': ID of the slice.
            Each dictionary contains the 'name' and 'id' of the slice.
    """
    return {
        'dataset_name': table.table_name,
        'dataset_id': table.id,
        'db_engine_spec': table.db_engine_spec,
        'dashboard_id': _parse_dashboard_id_from_url(request.url),
        'slice_id': _parse_slice_id_from_url(request.url),
    } if current_app.config.get('QUERY_ANNOTATIONS', False) else {}


def _is_bigquery(db_engine_spec) -> bool:
    from superset.db_engine_specs.bigquery import BigQueryEngineSpec
    return db_engine_spec == BigQueryEngineSpec


def annotate_query(sql: str, context: Dict, username: str) -> Optional[str]:
    """
    Generate an annotation based on the given context and adds it to the query.

    Args:
        sql (str): The query.
        context (Dict): The context containing information for generating the annotation.
        username (str): User executing the query.

    Returns:
        Optional[str]: Annotated query.
    """
    if not sql or not context or not current_app.config.get('QUERY_ANNOTATIONS', False):
        return sql
    db_engine_spec = context.get('db_engine_spec')
    if not db_engine_spec:
        return sql

    if _is_bigquery(db_engine_spec):
        return _generate_bigquery_annotation(sql, context, username)
    else:
        return sql


def _generate_bigquery_annotation(sql: str, context: Dict, username: str) -> str:
    """
    Generate a BigQuery annotation based on the given context and adds it to the query.

    Args:
        sql (str): The query.
        context (Dict): The context containing dataset_id, dashboard_id, and slice_id.
        username (str): User executing the query.

    Returns:
        Optional[str]: Annotated BigQuery annotation string
    """
    parts = ['--src:superset']
    dataset_id = context.get('dataset_id')
    if dataset_id:
        parts.append(f'--dataset_id:{dataset_id}')

    dashboard_id = context.get('dashboard_id')
    if dashboard_id:
        parts.append(f'--dashboard_id:{dashboard_id}')

    slice_id = context.get('slice_id')
    if dashboard_id:
        parts.append(f'--slice_id:{slice_id}')

    parts.append(sql)
    return "\n".join(parts)
