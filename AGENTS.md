Add unit tests whenever you add code

If you fix a bug, then add units tests to ensure that issue can never regress again

Update ADRs whenever you make a design decision. Update ADRs whenever  you change an existing design decision.

Rules for writing Marimo Notebooks:
- Remember that variables cannot redeclared in different cells, unless they start with an underscore. Use vars like `_a` and `_b` for variables in cells that other cvells don't need to access.
- If the cell only has markdown, use a markdown cell, not mo.md("...") to write the markdown.

In Marimo Notebooks, When writing code for dynamically rendering markdown, gm.md(t"""$some latex$ {var} some text""")
- include "import galaga_marimo as gm" in the imports of the notebook.
- Use triple quotes to write multi-line markdown.
- Use $ for inline math and $$ for display math.
- Use {var} to insert the value of a variable into the markdown. It will be rendered as latex.

Never use `git commit --amend` or `git push --force` (or `--force-with-lease`). Always create new commits.

Working with Geometric Algebra code:
- **Compute first, code second.** Run the algebra to get ground truth before writing any display/naming code.
- **Never hardcode what can be derived.** If a value depends on the metric, compute it from the metric.
- **Test against the algebra, not against your expectations.** The `TestSignConsistency` pattern (compute the product, compare to the stored sign) should be the first test, not the last.
- **Verify external claims with code.** Don't trust any identity — run it.
