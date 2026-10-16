# boolish 1.0.0 certification report

Progress:
- [x] Branch `release/1.0.0` created from `main` (0.2.0, never published, de1327f; PyPI has 0.1.0)
- [x] Baseline gates run on 0.2.0
- [x] API review and 1.0.0 API changes (item 1)
- [x] Ground truth: fetched specifications and real parsers' output (item 7)
- [x] Errors, typing, docstrings and doctests (items 2 to 5)
- [x] Contract, fuzz and author mutation round (items 6, 9, 18)
- [x] Docs: README, GUIDE, CHANGELOG (items 11, 12)
- [x] Packaging, e2e and upgrade from PyPI 0.1.0, author pass (items 8, 13, 14)
- [x] Every interpreter on this PC (item 10)
- [x] Five QA lenses report PASS (item 19)
- [ ] Independent reviewer (item 16)
- [ ] Gates (item 15)
- [ ] PR open and trace guard CLEAN (item 17); merge and publish left to the maintainer

## Baseline on 0.2.0 (before any change)

Run on a fresh clone of `main` (de1327f) on Elena's PC, Python 3.14.2.

| Command | Result |
| --- | --- |
| `ruff format --check .`, `ruff check .` | exit 0 |
| `mypy --strict src tests` | 4 errors (stale `type: ignore` codes in the contract test) |
| `pytest` | 95 passed (the end-to-end module built a venv and installed from the network on every run) |
| doctests | never run by the suite |

## Ground truth (item 7)

Two kinds of truth, none of them this library's own output.

- **Real parsers' answers** (`tests/fixtures/oracles.json`, captured 2026-10-16 by
  `scripts/capture_oracles.py` under CPython 3.11.5 in a throwaway virtual environment).
  The script calls each tool as it is on a hand-written corpus of 286 inputs (words of
  every vocabulary, case and whitespace variants, near misses, numbers, empty and
  full-width text; the corpus is labelled hand-written): the stdlib
  `distutils.util.strtobool` (the script refuses setuptools' substitute), setuptools
  84.0.0's `setuptools._distutils.util.strtobool`, python-strtobool 1.0.3,
  `configparser.RawConfigParser.getboolean`, click 8.5.0's `BOOL`, PyYAML 6.0.3 (YAML 1.1)
  and ruamel.yaml 0.19.1 (YAML 1.2). `tests/test_ground_truth.py` proves: `CLASSIC`
  answers exactly what the three stdlib-family tools answer on the stripped input; no
  vocabulary of boolish ever contradicts any of the seven tools; `DEFAULT` accepts
  everything any of them accepts except the blank values click 8.5 reads as false. Two
  oracles are also asked live: `configparser` on every interpreter, and `distutils` on
  Python 3.10 and 3.11.
- **Fetched specifications** (`scripts/fetch_sources.py`, 2026-10-16; the copies stay
  local and git-ignored, `tests/sources/MANIFEST.json` records URL, date, size, SHA-256
  and licence; the tests skip without them): CPython 3.11's `Lib/distutils/util.py`
  (pinned commit; its two word tuples, read with `ast`, equal `CLASSIC`), the YAML 1.1
  boolean type page (its regular expression's 22 spellings parse with their meaning), the
  YAML 1.2.2 core schema line (`true | True | TRUE | false | False | FALSE`), the CLDR
  POSIX yes/no strings for en, es, fr, de, it and pt (pinned commit; every full word
  parses leniently with `MULTILINGUAL`, and the one-letter answers left out are exactly
  `s`, `o` and `j`), and PEP 632 (deprecated in 3.10, gone in 3.12, as the README says).

Defects of 0.2.0 found against this truth and the promise review: `BoolRules(true="yes")`
split the word into letters; `to_bool` on a huge integer leaked the interpreter's own
`ValueError` from `repr`; error messages echoed whole inputs; lenient folding took time
quadratic in the length of a run of accented letters (a CPython `normalize` property,
now worked around in chunks); `getenv_bool(name, rules=...)` without a default did not
type-check; the CLI exited 1 both for false and for an error; `release.ps1` refused to
publish any project that already existed on PyPI.

## API review (items 1 to 5)

Kept from 0.1.0 and 0.2.0: every name, signature and default (`strtobool`, `to_bool`,
`is_truthy`, `is_falsy`, `getenv_bool`, `BoolRules` with positional `true` and `false`,
`DEFAULT`, `MULTILINGUAL`, `BoolLike`, `BoolishError`, `NotBooleanError`). Added for
1.0.0: `CLASSIC`, `NotBooleanError.variable`, `python -m boolish`, `--rules classic`.
Changed: CLI exit code 2 for unrecognised input; `TypeError` for non-string `strtobool`
input and for bare-string or non-string vocabulary words; bounded error messages;
`BoolRules.true`/`false` typed `frozenset[str]`, the folded sets private; the public
classes report `boolish` as their module. Every change is in CHANGELOG 1.0.0 with an
upgrade note from 0.1.0. `__all__` lists the twelve public names and `dir(boolish)` shows
nothing else public (`tests/test_contract.py`, which also freezes every signature).
Every public function and class has a `>>>` example and the constants and `BoolLike` have
one in the package docstring; `tests/test_docs.py` runs every module's doctests, every
README and GUIDE `pycon` block, and every `console` transcript. `mypy --strict src tests`
is clean; no `Any` in the public API.

## Author mutation round (item 18)

Each mutation was applied alone to a fresh clone at 54a21a6, the suite run with `-x` and
no bytecode (the end-to-end module skips without `BOOLISH_E2E=1`); the suite was green
before. 40 mutations: 39 killed at once; N04 survived and turned out to guard nothing,
so the redundant code went and a contract now pins the property that makes it redundant.

| Id | Mutation | File | Result | Caught by |
| --- | --- | --- | --- | --- |
| N01 | strict normalisation drops strip | `_normalize.py` | killed | `tests/test_docs.py::test_pycon_examples_run_and_print_what_they_show[README.md]` |
| N02 | strict normalisation drops lower | `_normalize.py` | killed | `tests/test_cli.py::test_classic_rules_and_repeated_words` |
| N03 | chunk loses its last character | `_normalize.py` | killed | `tests/test_fuzz.py::test_chunked_folding_equals_whole_string_folding[0]` |
| N04 | fold strips marks only once | `_normalize.py` | survived, then removed | the second pass was redundant: `tests/test_fuzz.py::test_folding_every_code_point_is_idempotent_and_mark_free` proves one pass leaves no mark on any code point, so the code now folds once |
| N05 | fold does not strip whitespace | `_normalize.py` | killed | `tests/test_fuzz.py::test_chunked_folding_equals_whole_string_folding[0]` |
| N06 | marks kept | `_normalize.py` | killed | `tests/test_cli.py::test_lenient_folds_accents` |
| P01 | lenient folded sides swapped | `_parse.py` | killed | `tests/test_cli.py::test_lenient_folds_accents` |
| P02 | lenient branch taken in strict mode | `_parse.py` | killed | `tests/test_cli.py::test_lenient_folds_accents` |
| P03 | false answers fall through | `_parse.py` | killed | `tests/test_docs.py::test_module_doctests_pass[boolish]` |
| P04 | non-string check dropped | `_parse.py` | killed | `tests/test_docs.py::test_pycon_examples_run_and_print_what_they_show[GUIDE.md]` |
| P05 | strict false side checked first and wins | `_parse.py` | killed | `tests/test_cli.py::test_true_value_prints_true_and_exits_zero` |
| C01 | infinity counts as finite | `_coerce.py` | killed | `tests/test_promises_parse.py::test_nan_and_infinity_are_never_boolean[inf]` |
| C02 | lenient numbers are false | `_coerce.py` | killed | `tests/test_docs.py::test_pycon_examples_run_and_print_what_they_show[GUIDE.md]` |
| C03 | floats not accepted | `_coerce.py` | killed | `tests/test_docs.py::test_module_doctests_pass[boolish]` |
| C04 | subclass equality trusted | `_coerce.py` | killed | `tests/test_promises_parse.py::test_number_subclasses_are_read_by_value` |
| C05 | is_falsy is a negation | `_coerce.py` | killed | `tests/test_docs.py::test_module_doctests_pass[boolish._coerce]` |
| C06 | default ignored by to_bool | `_coerce.py` | killed | `tests/test_docs.py::test_module_doctests_pass[boolish._coerce]` |
| E01 | empty variable read as unset | `_env.py` | killed | `tests/test_docs.py::test_pycon_examples_run_and_print_what_they_show[GUIDE.md]` |
| E02 | variable not named in the error | `_env.py` | killed | `tests/test_docs.py::test_module_doctests_pass[boolish._env]` |
| R01 | preview one character longer | `_errors.py` | killed | `tests/test_cli.py::test_the_error_message_is_one_bounded_line` |
| R02 | no ellipsis on cut strings | `_errors.py` | killed | `tests/test_cli.py::test_the_error_message_is_one_bounded_line` |
| R03 | big int bound off by one | `_errors.py` | killed | `tests/test_promises_rules.py::test_messages_show_a_bounded_preview[-18446744073709551615--18446744073709551615]` |
| R04 | type name cut later | `_errors.py` | killed | `tests/test_promises_rules.py::test_messages_show_a_bounded_preview` (the type-name case) |
| R05 | error pickling loses the value | `_errors.py` | killed | `tests/test_promises_rules.py::test_errors_survive_pickling` |
| U01 | bare strings accepted | `_rules.py` | killed | `tests/test_promises_rules.py::test_a_bare_string_is_refused_everywhere[yes0]` |
| U02 | non-string words accepted | `_rules.py` | killed | `tests/test_promises_rules.py::test_a_word_that_is_not_a_string_is_refused[1]` |
| U03 | overlap allowed | `_rules.py` | killed | `tests/test_cli.py::test_clashing_custom_words_are_an_error_with_exit_two` |
| U04 | folded collision allowed | `_rules.py` | killed | `tests/test_promises_basic.py::test_boolrules_rejects_accent_collision` |
| U05 | clash listing shows eleven | `_rules.py` | killed | `tests/test_promises_rules.py::test_clash_messages_stay_short` |
| U06 | extend puts true words on the false side | `_rules.py` | killed | collection of `tests/test_cli.py` (`MULTILINGUAL` no longer builds) |
| U07 | DEFAULT loses disabled | `_rules.py` | killed | `tests/test_contract.py::test_default_adds_enable_and_disable` |
| U08 | MULTILINGUAL loses nein | `_rules.py` | killed | `tests/test_contract.py::test_multilingual_vocabulary_is_pinned` |
| U09 | repr unsorted | `_rules.py` | killed | `tests/test_docs.py::test_module_doctests_pass[boolish]` |
| L01 | unrecognised exits 1 | `_cli.py` | killed | `tests/test_cli.py::test_unrecognised_value_goes_to_stderr_and_exits_two` |
| L02 | quiet ignored | `_cli.py` | killed | `tests/test_cli.py::test_quiet_prints_nothing_but_keeps_the_exit_code` |
| L03 | unencodable output raises | `_cli.py` | killed | `tests/test_cli.py::test_output_survives_a_stream_that_cannot_encode` |
| L04 | classic maps to default | `_cli.py` | killed | `tests/test_cli.py::test_classic_rules_and_repeated_words` |
| L05 | custom words ignored | `_cli.py` | killed | `tests/test_cli.py::test_custom_words` |
| L06 | closed pipe not redirected | `_cli.py` | killed | `tests/test_cli.py::test_a_closed_output_pipe_keeps_the_exit_code` |
| L07 | lenient flag inverted | `_cli.py` | killed | `tests/test_cli.py::test_lenient_folds_accents` |

## Supported Pythons (item 10)

The wheel built from a fresh clone (2a445e9), installed in a clean venv per interpreter on
this PC, the suite run from the extracted sdist with `src` removed (`-o pythonpath=`),
imports confirmed from site-packages; repeated by lens d at b6466e1:

| Python | Author pass (2a445e9) | Lens d (b6466e1) |
| --- | --- | --- |
| 3.10.19 | 296 passed, 3 skipped | 313 passed, 17 skipped |
| 3.11.5 | 296 passed, 3 skipped | 313 passed, 17 skipped |
| 3.12.12 | 295 passed, 4 skipped | 312 passed, 18 skipped |
| 3.13.2 | 295 passed, 4 skipped | 312 passed, 18 skipped |
| 3.14.2 | 295 passed, 4 skipped | 312 passed, 18 skipped |
| 3.14.2 free-threaded | 295 passed, 4 skipped | 312 passed, 18 skipped |

Skips: the three end-to-end tests without `BOOLISH_E2E=1` (run separately: 3 passed),
the live `distutils` test from 3.12 on, and in lens d's run the source tests without the
fetched copies. 3.9.25 is refused by `requires-python`; 3.8 is below it.

## Packaging and end-to-end (items 8, 13, 14)

`tests/test_e2e.py` (`BOOLISH_E2E=1`) builds both archives, runs `twine check --strict`,
checks the wheel holds only the package, `py.typed` and LICENSE and the sdist only the
project's own files plus the sources manifest, installs the wheel in a clean venv and
drives the console script and `python -m boolish` by subprocess (outputs, stderr, exit
codes 0, 1 and 2, `--version`), and upgrades boolish 0.1.0 from PyPI in place (`pip
check` clean). Lens d repeated all of it independently, added a `mypy --strict` consumer
of every public name against the installed wheel and compared about 130 probes between
0.1.0 and 1.0.0; every difference is in CHANGELOG 1.0.0's upgrade section.

## Independent QA lenses (item 19)

Each lens was a fresh, independent review that read the certification checklist first,
ran things rather than reading them, worked in its own clone and reported back only.

| Lens | Round | Head | Verdict | Findings and outcome |
| --- | --- | --- | --- | --- |
| a. API and docs | 1 | 2a445e9 | FAIL (3 medium, 4 low, 2 info) | a `--help` example failed; `--lenient` help promised numbers; the folded-collision refusal and the 0.1.0 `bytes` behaviour missing from the upgrade notes; 0.2.0-only changes mixed into the 1.0.0 list; folded sets visible through `dataclasses.fields`; docstring examples leaning on module globals; the default sentinel printed as an address and functions reporting private modules; help wider than 80 columns. Fixed in 3ec60e4 |
| a | 2 | 3ec60e4 | PASS (1 low) | all nine fixed; one help line misaligned, fixed in be46d9f |
| b. Correctness and ground truth | 1 | be46d9f | PASS | 82,272 inputs against the stdlib function on 3.10 and 3.11 with 0 mismatches; 12 tools (adding pydantic, marshmallow, environs and str2bool) with 0 contradictions; MULTILINGUAL words checked against CLDR and dictionary entries; `oracles.json` re-captured with 0 differences; manifest hashes match |
| c. Adversarial and robustness | 1 | be46d9f | FAIL (1 high, 3 medium, 3 low, 1 info) | a closed stdout or stderr turned the exit code into 1; NFKD-expanding input made lenient matching take 10 s for 10^6 characters; overriding subclasses and mocks faking `__class__` broke calls; control characters from type names and argparse; `--help` crashed on cp932; `getenv_bool` messages showed part of the value. About 800,000 fuzz cases otherwise clean, threads clean on 3.14t. Fixed in 5ab7223 |
| c | 2 | 5ab7223 | FAIL (2 low) | all eight fixed; 750,000 seeded cases prove the early stop never changes an answer; the chained inner error still held a preview of the variable's value; a metaclass `__name__` property broke the type name. Fixed in b6466e1 |
| c | 3 | b6466e1 | PASS | both fixed; `getenv_bool` matches `strtobool` on every probe |
| d. Packaging and real e2e | 1 | b6466e1 | PASS (1 low, 2 info) | interpreter matrix above, archives, metadata, CLI, typed consumer, upgrade; two 0.1.0 differences (overriding `str` subclasses, objects with `strip`) missing from the upgrade notes; release script nits. Fixed in f516082 and 7604af4 |
| d | 2 | f516082 | PASS | both confirmed against PyPI 0.1.0 |
| e. Contract strength (blind) | 1 | 7604af4 | FAIL | 83 mutations: 71 killed, 4 equivalent, 8 survived (lenient limit one short, lying float `__eq__`, the non-string size in environment errors, the clash listing bound, the CLI default vocabulary, the usage-error cut and its ellipsis, the encoding fallback). Contracts in `tests/test_contract_strength.py` (2268829), each survivor re-applied and killed |
| e | 2 | 2268829 | PASS | the eight re-applied survivors killed; `src` unchanged since round 1, so 15 fresh mutations on the new contracts' targets: all killed |

Equivalent mutations argued by lens e: the chunk size (decomposition is per character and
every reordered mark is dropped), the ASCII fast path (NFKD leaves ASCII unchanged), passing
a `str` subclass on (both matchers call `str.strip` first), and the `bool` branch (the
integer path gives the same answer).
