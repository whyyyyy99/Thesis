    return pl.read_csv(stream, 
                       dtypes={'age': int,
                               'qx': float,
                               'gender': str})
