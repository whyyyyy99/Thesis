        data = self.get_data(*args, **kwargs)
        return pl.DataFrame(data, schema=columns)
