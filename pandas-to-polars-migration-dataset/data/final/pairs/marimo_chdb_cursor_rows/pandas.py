            rows = self._cursor.fetchall()
            col_names = self._cursor.column_names()
            return pd.DataFrame(rows, columns=col_names)
