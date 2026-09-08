"""Keep the root Marimo entrypoint out of ordinary pytest collection.

It uses Python 3.14 t-strings and is executed by the maintained notebook suite,
not imported as a test module on every supported Python version.
"""

collect_ignore = ["test_mermaid.py"]
