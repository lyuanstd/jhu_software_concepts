from decimal import Decimal
from query_data import format_value, format_row, get_queries


def test_format_value_converts_decimal_to_string():
    value = Decimal("3.79")
    result = format_value(value)
    assert result == "3.79"

def test_format_value_converts_integer_to_string():
    value = 33040
    result = format_value(value)
    assert result == "33040"

def test_format_value_converts_none_to_string():
    value = None
    result = format_value(value)
    assert result == "None"

def test_format_row_joins_multiple_values():
    row = ("Johns Hopkins University", 18, Decimal("35.83"))
    result = format_row(row)
    assert result == "Johns Hopkins University, 18, 35.83"

def test_get_queries_returns_list_of_query_dicts():
    queries = get_queries()

    assert isinstance(queries, list)
    assert len(queries) > 0
    assert "question" in queries[0]
    assert "sql" in queries[0]