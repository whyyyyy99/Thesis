            rows = self._cursor.fetchall()
            col_names = self._cursor.column_names()
            return self._convert_to_output_format(
                sql_output_format, rows, col_names
            )
