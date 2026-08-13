# Baseline Test Notebook Audit Report

**Scope**: 238 migration pairs · 128 baseline notebooks · 261 functions  
**Method**: Full scan — all notebooks, all functions, cross-referenced with source `*_before.py` and `*_before_after_generated.py` files  

---

## 0. Coverage (D0)

**All 238 pairs are covered** — confirmed via sha8 lookup across both flat `test/` dirs and `test/{sha8}/` subdirs.

- 152 pairs: sha8-prefixed `func_id` → directly in `test/{sha8}/` subdirectory  
- 86 pairs: function-name-only `func_id` → in flat `test/` or `test/{sha8}/` via sha from results.jsonl  
- 0 pairs without a notebook  

---

## 1. Gen Code Integrity (D1)

After normalization (dedent, strip `import` lines, strip `pd = pl` aliases, strip `if param is None:` guards, strip trailing `return None`):

- ✅ Logic-identical to source: ~209 functions  
- ⚠️ Style-only diff (trivial variable rename, `return result` added, `pass` in loop): **6**  
- ❌ Alternative implementation or stub: **12**  

### D1 High-severity issues (ALT_IMPL / STUB)

| Notebook | Function | Category | Detail |
|---|---|---|---|
| `1f8af3a3_target_elusive_test.ipynb` | `unbinned` | ALT_IMPL | `.with_row_index().rank()` vs source `.group_by().first()` — different algorithm |
| `1f8af3a3_target_elusive_test.ipynb` | `sample_pairs` | ALT_IMPL | Cross join approach vs `group_by+map_groups` — fundamentally different |
| `1f8af3a3_target_elusive_test.ipynb` | `sparse_edges` | ALT_IMPL | Groups by `["sample","sample_2"]` vs source `["sample_pairs"]` |
| `83c12695_collect_reference_bins_test.ipynb` | `collect_pivot` | ALT_IMPL | Refactored as `return df.with_columns(...)` instead of `appraise_binned = ...` |
| `92e35040_query_processing_test.ipynb` | `binned_unbinned` | ALT_IMPL | NB extracts body directly; source wraps with `def before_binned_unbinned` (nested def) |
| `f11c29ae_cate_dataset_test.ipynb` | `dataset_save_load` | STUB | `raise NotImplementedError("snippet is a class method body...")` — gen code never executed |
| `99aff9e0_polars_bio_range_op_io_test.ipynb` | `rename_columns_empty_df` | ALT_IMPL | Different branch structure with `elif pd` clause; causes `UnboundLocalError` at runtime |
| `3c49cad1_benchmarks_timeseries_test.ipynb` | `rmse` | ALT_IMPL | NB: `n=s1.len()` then `(s1-s2).drop_nulls()**2`; source: `get_rmse()` inner def |
| `3c49cad1_benchmarks_timeseries_test.ipynb` | `timeseries_extract` | ALT_IMPL | NB: `return df.with_columns(...)` (pure return); source: `param_data.values = ...` (side-effect) |
| `3c49cad1_benchmarks_timeseries_test.ipynb` | `geosphere_collect` | ALT_IMPL | NB simplified dict comprehension; source: `json.loads(response.read())` stream parsing |
| `3c49cad1_benchmarks_timeseries_test.ipynb` | `geosphere_all` | ALT_IMPL | NB: `pl.read_csv(io.StringIO(...))` + `drop/rename`; source: `pd.read_csv(response)` + `{RENAME_MAP}` (set literal bug in source) |
| `3c49cad1_wetterdienst_provider_dwd_radar_index_test.ipynb` | `radar_index_sweeps` | ALT_IMPL | NB: polars `.str.ends_with()`; source gen: pandas `.str.endswith()` pattern |

### Legitimate additions (NOT tampering)

These are harness-only additions found in many notebooks:
- `pd = pl  # LLM used 'import polars as pd'` — necessary to run LLM code that confused namespace
- `if param is None: param = pl.DataFrame(...)` — inline default fixture guard  
- `return result_var` added at end — wrapper needs to return value for comparison
- Import lines stripped from wrapper body — not part of snippet logic

---

## 2. Before Code Alignment (D2)

- ✅ Logic-identical to `*_before.py` source: ~208 functions  
- ⚠️ Style-only diff (dedent, minor variable rename): **6**  
- ❌ Empty before wrapper / before wrapper missing: **9 functions across 3 notebooks**  
- ❌ Before logic changed: **3 functions**  

### D2 Missing/empty before wrappers

| Notebook | Functions | Issue |
|---|---|---|
| `1f8af3a3_target_elusive_test.ipynb` | `unbinned`, `sample_pairs`, `sparse_edges` | Hand-crafted notebook — `before_*` wrappers completely absent; no pandas-side test |
| `83c12695_collect_reference_bins_test.ipynb` | `collect_pivot` | `before_collect_pivot` wrapper body is empty (passes but tests nothing) |
| `3c49cad1_benchmarks_timeseries_test.ipynb` | `interp_filter`, `timeseries_extract`, `geosphere_collect`, `geosphere_all`, `radar_sites_cols` | Hand-crafted notebook — these functions only have `gen_*`; no before comparison possible |

### D2 Logic changes

| Notebook | Function | Issue |
|---|---|---|
| `8017f91b_readnext_evaluation_scoring_hybrid_score_test.ipynb` | `hybrid_score_frame` | before body replaced `...` with `pd.DataFrame({"document_id":[0],"score":[0.9]})` — this is the fix we applied; ✅ correct |
| `99aff9e0_polars_bio_range_op_io_test.ipynb` | `rename_columns_empty_df` | before wrapper also uses different branching logic from source |
| `3c49cad1_wetterdienst_provider_geosphere_observation_api_test.ipynb` | `geosphere_all` | Source has `{GEOSPHERE_RENAME_MAP}` (set literal — bug in source); NB has `GEOSPHERE_RENAME_MAP` (correct dict) — NB is better |

---

## 3. Fixture Type Correctness (D3)

**40 functions** where gen wrapper uses polars-only API but receives a pandas DataFrame fixture.

This causes false gen L1 failures (HARNESS_TYPE, not GEN_BUG).

### Full list

| Notebook | Functions | Root cause |
|---|---|---|
| `05afd878_ibis_workflow_scripts_evaluate_test.ipynb` | `evaluate_coassembly_edges`, `evaluate_combined`, `evaluate_nontarget`, `evaluate_unbinned` | `FIX_*` are `pd.DataFrame()`; gen calls `.with_columns()`, `.join()` etc. |
| `1f8af3a3_ibis_workflow_scripts_target_elusive_test.ipynb` | `target_elusive_sample_pairs`, `target_elusive_unbinned` | Same |
| `92e35040_ibis_workflow_scripts_query_processing_test.ipynb` | `query_binned_unbinned` | Same |
| `e75a38b6_src_quant_trading_strategy_backtester_backtester_test.ipynb` | `quant_backtester_calculate_returns_migration` | `self.data = pd.DataFrame()`; gen calls `self.data.with_columns()` |
| `04dc43a8_vnc_networks_cmatrix_test.ipynb` | `vnc_cmatrix_loc_filter_item`, `vnc_cmatrix_lookup_init`, `vnc_cmatrix_reindex`, `vnc_cmatrix_uid_to_index` | `self.lookup = pd.DataFrame()`; gen calls `.filter()`, `.select()` |
| `001df316_src_scoring_test.ipynb` | `scoring_compare_methylation_pattern_migration`, `scoring_compare_methylation_pattern_multiprocessed_migration`, `scoring_define_mean_methylation_thresholds_migration` | Fixtures are pandas; gen uses polars `.with_columns()` chain |
| `f11c29ae_cate_dataset_test.ipynb` | `dataset_df_clone`, `dataset_loc_select` | `FIX_CATE_DATA_PD` passed to gen which calls `.with_columns()` |
| `a52cebfe_src_ert_analysis__es_update_test.ipynb` | `es_update_scaling_factors` | `FIX_*` is list of `pd.DataFrame`; gen calls `pl.concat()` |
| `a52cebfe_src_ert_resources_workflows_jobs...test.ipynb` | `rft_concat_write`, `rft_obs_join` | `FIX_*` are `pd.DataFrame`; gen uses polars methods |
| `e8fa7691_src_ert_gui_simulation__design_matrix_panel_test.ipynb` | `design_matrix_model` | Same pattern |
| `e5f9fa83_acryo_loader_test.ipynb` | `acryo_loader_corr_max_with_columns_migration`, `acryo_loader_update_features_migration` | Same |
| `e5f9fa83_acryo_molecules_test.ipynb` | `acryo_molecules_concat_migration`, `acryo_molecules_from_csv_migration`, `acryo_molecules_to_dataframe_migration` | Same |
| `8cd8fa4e_src_onemod_utils_parameters_test.ipynb` | `src_onemod_utils_parameters_create_params_migration` | Same |
| `8017f91b_readnext_evaluation_scoring_precompute_scores_test.ipynb` | `precompute_cross_join` | Same |
| `8c71f3c7_readnext_inference_input_converter_test.ipynb` | `input_converter_loc` | `self.documents_data = pd.DataFrame()`; gen calls `.filter()` |
| `0ac0c862_medmodels_matching_algorithms_classic_distance_models_test.ipynb` | `medmodels_classic_distance_covariates_select_migration`, `medmodels_classic_distance_match_migration` | Polars fixture has string "patient_id" col; both sides call `.astype(float)` → ValueError |
| `0ac0c862_medmodels_matching_algorithms_propensity_score_test.ipynb` | `medmodels_propensity_score_prop_score_migration` | Same |
| `16645382_actxps_exp_stats_test.ipynb` | `exp_stats_col_assign` | Same |
| `397aab66_mexca_data_test.ipynb` | `mexca_data_merge_features_migration` | Same |
| `ad8e199f_portfolio_python_api_statistical_indicators_momentum_indicators_test.ipynb` | `portfolio_momentum_roc`, `portfolio_momentum_rsi`, `portfolio_momentum_stoch_osc`, `portfolio_momentum_stoch_rsi` | `self.df = pd.DataFrame()`; gen calls `.with_columns()` |
| `efc0581f_src_img2table_ocr_data_test.ipynb` | `data_assign_bbox`, `data_merge_cross` | `self.df = pd.DataFrame()`; gen calls polars API |

**Fix pattern**: For each of these, add split fixtures:  
```python
FIX_FUNCNAME_BEFORE = pd.DataFrame(...)   # pandas for before_*
FIX_FUNCNAME_GEN    = pl.DataFrame(...)   # polars for gen_*
```

---

## 4. Fixture Quality (D4)

Spot-check findings:

| Issue | Affected notebooks | Detail |
|---|---|---|
| String column in numeric-expected fixture | `0ac0c862_medmodels_classic_distance_models` | `patient_id` column is `str`; code calls `.to_numpy().astype(float)` → both before and gen fail |
| `Ellipsis ...` placeholder | `8017f91b_readnext_evaluation_scoring_hybrid_score_test.ipynb` | Was `"..."` as fixture; **fixed** in prior session |
| Incomplete mock objects | `a52cebfe_src_ert_analysis__es_update_test.ipynb` | `ensemble = 1` (int); before calls `.save_observation_scaling_factors()` → AttributeError |
| Single-row fixtures | Multiple | Only 1 row → row-order tests meaningless; minor |
| `radar_sites_cols` fixture missing required cols | `3c49cad1_wetterdienst_provider_dwd_radar_sites_test.ipynb` | Fixture has `coordinates_wgs84` but wrapper does `data.insert(4, "longitude", ...)` which expects positional column count |

---

## 5. L1/L2/L3 Label Correctness (D5)

**0 mixed-label issues found** (no `L2 equivalence L3 ...` pattern in any notebook).

Consistent patterns across all auto-generated notebooks:
- L1: `✅ L1 smoke gen_*` / `✅ L1 smoke before_*` — correct  
- L2: `✅ L2 equivalence *: MATCH` / `❌ L2 equivalence *: MISMATCH` — correct  
- Skip: `⚠️  L2 skip *: both sides non-DataFrame` — correctly labeled  
- L3: `✅ L3 edge *: ran without crash` — correct  

**One systemic L3 quality issue** (not a label error, but a semantic gap): the boilerplate L3 template  
```python
gen_func(pl.DataFrame({c: [] for c in FIX.columns}) if isinstance(FIX, pl.DataFrame) else FIX)
```
passes the **identical fixture** when `FIX` is not a DataFrame (strings, ints, SimpleNamespace) — L3 becomes identical to L1 and tests nothing extra.

---

## 6. Tests Actually Call the Code (D6)

**8 factory-pattern functions** where L3 calls the outer `gen_func()` again instead of calling the inner function it returns:

| Notebook | Function | What L3 does | What it should do |
|---|---|---|---|
| `334c4e69_src_quant_trading_strategy_backtester_data_test.ipynb` | `quant_trading_strategy_backtester_data_load_yfinance_data_two_tickers_migration` | Calls `gen_func()` again | Call returned inner `load_yfinance_data_two_tickers(ticker, ...)` |
| `b36214f9_triplifier_data_descriptor_utils_data_preprocessing_test.ipynb` | `preprocess_attrs_registry` | Calls `gen_func()` again | Call returned `preprocess_dataframe(df)` |
| `04dc43a8_vnc_networks_cmatrix_test.ipynb` | `vnc_cmatrix_sort_tolist` | Calls `gen_func()` again | Call returned `get_uids(sub_indices, axis)` |
| `e3227f4f_cate_dataset_test.ipynb` | `split_empty_df` | Calls `gen_func()` again | Call returned `split(ds, test_frac=...)` |
| `8017f91b_readnext_utils_io_test.ipynb` | `io_parquet` | Calls `gen_func()` again | Call returned `read_parquet(path)` |
| `325e7c2b_actxps_dates_test.ipynb` | `dates_pol_interval` | Calls `gen_func()` again | Call returned `pol_interval(...)` |
| `397aab66_mexca_data_test.ipynb` | `mexca_data_delete_filename_time_col_migration` | Calls `gen_func()` again | Call `_r(df)` on returned static method |
| `397aab66_mexca_data_test.ipynb` | `mexca_data_merge_video_annotation_migration` | Calls `gen_func()` again | Call `_r(self, data_frames)` on returned method |

---

## 7. Failure Classification (D7)

Based on executed cell outputs:

| Category | Count (estimated) | Examples |
|---|---|---|
| **HARNESS_TYPE**: fixture type mismatch (pandas given to gen polars wrapper) | ~40 | All D3 cases above |
| **HARNESS_UNCALLED**: factory returned, inner never invoked in L3 | 8 | All D6 cases above |
| **GEN_BUG** (genuine API error): real LLM mistake | ~15 | `wetterdienst::noaa_ghcn` (`separator=r"\s+"` multi-byte), `ert::es_update_pivot_join` (join suffix), `pheval::gene_identifier_map` (`.iter_rows()` on pandas), `binchicken::evaluate` series |
| **GEN_LOGIC**: gen runs but produces different output | ~5 | Some binchicken/cate diffs visible in L2 MISMATCH |
| **BEFORE_CONTEXT**: before needs class/module context not provided | ~10 | `pairwise_metric` (undefined global `df`), `ert::es_update_scaling_factors` (`ensemble=1`) |
| **SETUP**: fixture cell crash or import error | ~3 | `img2table` Ellipsis cells, `polars-bio rename_columns` UnboundLocalError |
| **ORIGINAL_LIMITATION**: snippet is dead code / method body / not standalone | ~3 | `cate::dataset_save_load` (raise NotImplementedError), some wetterdienst |

---

## Summary Table

| Dimension | Status | Issues |
|---|---|---|
| D0 Coverage | ✅ | 0 missing pairs |
| D1 Gen integrity | ⚠️ | 12 ALT_IMPL/STUB, 6 style-only |
| D2 Before alignment | ⚠️ | 9 missing before wrappers, 2 logic changes |
| D3 Fixture type | ❌ | 40 functions with pandas fixture given to polars gen wrapper |
| D4 Fixture quality | ⚠️ | medmodels string-col bug, ert incomplete mock, some single-row fixtures |
| D5 Label correctness | ✅ | 0 mixed-label issues |
| D6 Code actually called | ❌ | 8 factory functions where L3 never calls inner fn |
| D7 Failure classification | ❌ | ~40 HARNESS_TYPE failures misclassified as GEN_BUG |

---

## Top Priorities for Fixes

1. **D3 (40 cases)**: Split fixtures into `FIX_*_BEFORE` (pandas) + `FIX_*_GEN` (polars) for all 40 affected functions  
2. **D6 (8 cases)**: In L3, call `_inner = gen_func(args); _inner(test_args)` instead of calling `gen_func()` again  
3. **D1 (12 cases)**: For ALT_IMPL — decide whether to accept alternative or restore source; for STUB — mark as `original_limitation` in failure CSV  
4. **D2 (9 cases)**: Add `before_*` wrappers to `1f8af3a3_target_elusive_test.ipynb` (3 fns) and `3c49cad1_benchmarks` (5 fns), or mark as intentional omissions  
5. **D4 medmodels**: Fix fixture to exclude `patient_id` column or use numeric-only columns  
6. **D7**: Re-classify ~40 HARNESS_TYPE failures in CSV once D3 is fixed  
