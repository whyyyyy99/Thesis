# Audit Material

`parse_failures.csv` is a filtered view of the stored formal comparison table. It identifies the 21 snippets for which AST construction failed and records their gold-set size, false-negative count, set-comparison outcome, and gold APIs.

The thesis groups the observed syntax problems into retained indentation, missing initial receivers in method chains, dangling continuations, incomplete compound statements, and malformed multiline expressions. Those causes were established through manual inspection. The archived comparison table does not contain a row-level reason field, so this release does not assign an undocumented reason label to individual snippets.
