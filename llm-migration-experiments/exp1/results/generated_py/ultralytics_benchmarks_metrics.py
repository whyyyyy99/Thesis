import math
import polars as pl

df = pl.DataFrame(y, schema=["Format", "Status❔", "Size (MB)", key, "Inference time (ms/im)", "FPS"])

name = model.model_name
dt = time.time() - t0
legend = "Benchmarks legend:  - ✅ Success  - ❎ Export passed but validation failed  - ❌️ Export failed"
display_df = df.with_columns(pl.all().cast(pl.Utf8).fill_null("-"))
s = f"\nBenchmarks complete for {name} on {data} at imgsz={imgsz} ({dt:.2f}s)\n{legend}\n{display_df}\n"
LOGGER.info(s)
with open("benchmarks.log", "a", errors="ignore", encoding="utf-8") as f:
    f.write(s)

if verbose and isinstance(verbose, float):
    metrics = df[key].to_list()
    floor = verbose
    assert all(
        x > floor
        for x in metrics
        if x is not None and not (isinstance(x, float) and math.isnan(x))
    ), f"Benchmark failure: metric(s) < floor {floor}"

return df
