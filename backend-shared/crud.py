import sqlite3
from fastapi import HTTPException, Response


def get_rows(db, table):
    return [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY id")]


def get_row(db, table, item_id):
    row = db.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Запись не найдена")
    return dict(row)


def save_row(db, table, data, item_id=None):
    columns = list(data)
    values = list(data.values())
    try:
        if item_id is None:
            marks = ", ".join("?" for column in columns)
            cursor = db.execute(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({marks})",
                values,
            )
            item_id = cursor.lastrowid
        else:
            get_row(db, table, item_id)
            fields = ", ".join(f"{column} = ?" for column in columns)
            db.execute(f"UPDATE {table} SET {fields} WHERE id = ?", [*values, item_id])
        db.commit()
        return get_row(db, table, item_id)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Проверьте данные")


def delete_row(db, table, item_id):
    get_row(db, table, item_id)
    try:
        db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
        db.commit()
        return Response(status_code=204)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Запись используется")
