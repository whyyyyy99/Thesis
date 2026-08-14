import pandas as pd

df_lines = pd.DataFrame(data=[line.dict for line in lines])
df_lines['length'] = pd.concat([df_lines['width'], df_lines['height']], axis=1).max(axis=1)
df_lines['vertical'] = (df_lines['x1'] == df_lines['x2'])
df_lines['line_id'] = range(len(df_lines))
df_lines.columns = ['x1_line', 'x2_line', 'y1_line', 'y2_line', 'width', 'height', 'length', 'vertical', 'line_id']
