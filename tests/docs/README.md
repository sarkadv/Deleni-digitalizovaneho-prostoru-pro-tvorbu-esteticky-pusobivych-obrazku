# Test suite

One set of tests for both implementations of the program: the original Python one and the C rewrite.

* [HOW_TESTS_WORK.md](HOW_TESTS_WORK.md) – how the tests work (backends, reference results)
* [TEST_SCENARIOS.md](TEST_SCENARIOS.md) – every test scenario and how its result is checked

## Running

```
pip install -r tests/requirements.txt          # plus requirements.txt (project root) for the Python program
pytest                                         # Python program (default, ~4 min)
pytest --backend=c --c-lib=build/libstylize.dylib --c-app=build/stylize     # C program
```

Give options with a path as `--option=value`: in the form `--option value` pytest takes the path for a
test location. The options can also be set as environment variables `STYLIZE_BACKEND`,
`STYLIZE_PYTHON_ROOT`, `STYLIZE_C_LIB` and `STYLIZE_C_APP`.

Tests never modify the program; they only seed its random generators.

## Regenerating test data

```
python tests/tools/make_test_images.py     # input pictures in tests/data/
python tests/tools/make_golden.py          # reference results in tests/golden/ (from the Python program, ~5 min)
```

Only needed when the inputs or the Python program's intended behaviour change.
