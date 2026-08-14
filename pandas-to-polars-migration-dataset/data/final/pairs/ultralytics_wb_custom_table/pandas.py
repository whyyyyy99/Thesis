    import pandas  # scope for faster 'import ultralytics'

    df = pandas.DataFrame({"class": classes, "y": y, "x": x}).round(3)
    ...
    return wb.plot_table(
        "wandb/area-under-curve/v0", wb.Table(dataframe=df), fields=fields, string_fields=string_fields
    )
