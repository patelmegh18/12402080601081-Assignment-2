import re

ALLOWED_COLUMNS = {
    "student.id": "s.student_id",
    "student.name": "s.name",
    "student.spi": "s.spi",
    "course.id": "c.course_id",
    "course.name": "c.course_name",
    "courseregistration.student_id": "r.student_id",
    "courseregistration.course_id": "r.course_id"
}

def validate_and_build(projection, raw_where, order_by, limit_val):
    selected = []
    for col in projection:
        key = col.strip().lower()
        if key not in ALLOWED_COLUMNS:
            raise ValueError(f"Invalid column name: {col}")
        selected.append(f"{ALLOWED_COLUMNS[key]} AS `{key}`")

    where_clauses = []
    params = []
    
    if raw_where:
        conditions = [cond.strip() for cond in re.split(r"\s+AND\s+", raw_where, flags=re.IGNORECASE)]
        for cond in conditions:
            match = re.match(r"^([a-zA-Z_.]+)\s*(>=|<=|!=|=|>|<|LIKE)\s*(.+)$", cond)
            if not match:
                raise ValueError(f"Malformed condition: {cond}")
            col, op, val = match.groups()
            col_key = col.strip().lower()
            if col_key not in ALLOWED_COLUMNS:
                raise ValueError(f"Invalid column in condition: {col}")
            
            where_clauses.append(f"{ALLOWED_COLUMNS[col_key]} {op.upper()} %s")
            params.append(val.strip().strip("'").strip('"'))

    order_clause = ""
    if order_by:
        parts = order_by.strip().split()
        ord_col = parts[0].lower()
        ord_dir = parts[1].upper() if len(parts) > 1 else "ASC"
        if len(parts) > 2 or ord_col not in ALLOWED_COLUMNS or ord_dir not in ("ASC", "DESC"):
            raise ValueError(f"Invalid ORDER BY: {order_by}")
        order_clause = f" ORDER BY {ALLOWED_COLUMNS[ord_col]} {ord_dir}"

    if not (1 <= limit_val <= 1000):
        raise ValueError("LIMIT must be between 1 and 1000")

    base_query = (
        "SELECT " + ", ".join(selected) +
        " FROM Student s"
        " INNER JOIN CourseRegistration r ON s.student_id = r.student_id"
        " INNER JOIN Course c ON r.course_id = c.course_id"
    )

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    
    base_query += order_clause
    base_query += f" LIMIT {int(limit_val)};"

    return base_query, params

if __name__ == '__main__':
    cols = ["student.name", "course.name"]
    condition = "course.id = PY101"
    order = "student.spi DESC"
    limit = 2

    try:
        sql, query_params = validate_and_build(cols, condition, order, limit)
        print("SQL_OK")
        print(f"Generated SQL: {sql}")
        print(f"Parameters: {query_params}")
    except ValueError as err:
        print(f"SQL_REJECTED: {err}")
