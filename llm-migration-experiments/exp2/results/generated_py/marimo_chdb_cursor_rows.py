rows = self._cursor.fetchall()
col_names = self._cursor.column_names()
return pl.DataFrame(rows, schema=col_names)