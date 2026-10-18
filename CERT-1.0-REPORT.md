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
- [x] Independent reviewer (item 16)
- [x] Gates (item 15)
- [x] PR #2 open and trace guard CLEAN (item 17); merge and publish left to the maintainer

## Scorecard (at the head of PR #2)

| # | Item | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | API reviewed for stability | PASS | every 0.1.0 name and signature kept; `CLASSIC`, `NotBooleanError.variable`, `python -m boolish` added; every change in CHANGELOG 1.0.0, compared side by side with PyPI 0.1.0 by lenses a and d (about 130 probes) |
| 2 | `__all__` exact | PASS | twelve names, nothing else public (`tests/test_contract.py`) |
| 3 | Docstrings with runnable examples | PASS | every public function and class runs its own example with empty globals; constants and `BoolLike` in the package docstring; README and GUIDE `pycon` blocks and `console` transcripts and every `--help` example run in `tests/test_docs.py` and `tests/test_cli.py` |
| 4 | Typed end to end | PASS | `mypy --strict src tests` clean; `py.typed` shipped; strict consumer of every public name against the installed wheel (lens d) |
| 5 | Typed, documented, safe errors | PASS | GUIDE error table; messages show at most 32 characters, sizes for huge integers, escaped type names, and only the length of environment values |
| 6 | Contract asserts the full promise | PASS | 323 tests: promises per public name, ground truth, fuzz, hostile input, CLI, and the contracts from the author, lens e and reviewer mutation rounds |
| 7 | Real ground truth | PASS | seven real parsers' answers captured from the tools themselves; CPython 3.11, YAML 1.1 and 1.2.2, CLDR and PEP 632 fetched with manifest; lens b re-derived it all with twelve tools and 82,272 stdlib comparisons |
| 8 | Real e2e incl. PyPI upgrade | PASS | `BOOLISH_E2E=1`: archives, installed wheel by subprocess, upgrade in place from PyPI 0.1.0 (author, lens d, reviewer) |
| 9 | Seeded fuzz, no crash, hang or blow-up | PASS | seeded fuzz, every-code-point folding check and linear-time tests in the suite; lens c: about 1.55 million fuzz cases and scaling to 10^7 characters |
| 10 | Every interpreter on this PC | PASS | 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2 and 3.14.2t from the installed wheel (author and lens d) |
| 11 | README | PASS | `twine check --strict`; absolute links; problem, verified why, install, quick start, GUIDE and CHANGELOG links |
| 12 | CHANGELOG dated 1.0.0 | PASS | `## [1.0.0] - 2026-10-16` with the stable surface and an upgrade list from 0.1.0 |
| 13 | pyproject | PASS | 1.0.0 (one source), Production/Stable, 3.10 to 3.14, MIT, Homepage/Source/Issues/Changelog, keywords, `dependencies = []` |
| 14 | sdist and wheel contents | PASS | wheel: package, `py.typed`, LICENSE; sdist: source, tests, fixtures, sources manifest, scripts, docs; no fetched third-party copy |
| 15 | Gates exit 0 alone | PASS | `ruff format --check .`, `ruff check .`, `mypy --strict src`, `pytest` on a fresh clone (reviewer, and again at the final head) |
| 16 | Independent reviewer | PASS | review 1 FAIL (three mutation survivors), review 2 PASS at 65d169e |
| 17 | PR, trace guard | ready | PR #2 from `release/1.0.0`, trace guard CLEAN; merge and PyPI publish left to the maintainer |
| 18 | Mutation round | PASS | author 40 (39 killed, 1 removed as redundant code); blind lens e 83 (71 killed, 4 equivalent, 8 closed by contracts) and 15 more, all killed; reviewer 8 re-applied and 40 new (34 killed, 3 equivalent, 3 closed by contracts) |
| 19 | Five QA lenses | PASS | a (round 2), b (round 1), c (round 3), d (round 2), e (round 2) |

## Behaviour changes against PyPI 0.1.0

The CHANGELOG's "Upgrading from 0.1.0" list is the reference; lenses a and d traced every
difference they measured to a line there. In short: `DEFAULT` also accepts
`enable(d)`/`disable(d)` (`CLASSIC` keeps the 0.1.0 words); errors are `NotBooleanError`
and `BoolishError`, still `ValueError`, with bounded messages; `strtobool` raises
`TypeError` for anything that is not a `str`; `BoolRules` refuses a bare string, a
non-string word and words that collide once folded; `str` subclasses are read by their
plain text; new `to_bool`, `is_truthy`, `is_falsy`, lenient mode, `MULTILINGUAL`,
`extend` and the `boolish` command.

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

## Independent reviewer (item 16)

| Review | Head | Verdict | Findings and outcome |
| --- | --- | --- | --- |
| 1 | d281a1f | FAIL (item 18) | every other item passed on its own evidence: gates alone on a fresh clone, 320 passed and 18 skipped, `BOOLISH_E2E=1` 3 passed, `twine check --strict`, archives, metadata, sources re-fetched with unchanged hashes, trace guard CLEAN; 8 author mutations re-applied and killed; 40 new mutations: 34 killed, 3 equivalent (the leading strip in `fold_within`, `isinstance` in `strtobool`, `str.__str__` before matching), 3 survived (a float subclass's own `__repr__`, an unbounded variable name, an unsorted clash listing). Contracts in `tests/test_contract_strength.py`, each survivor re-applied and killed; the old improvement plan now says 1.0.0 changed what it describes |
| 2 | 65d169e | PASS | the three survivors re-applied and killed; `src` unchanged since review 1; gates alone on a fresh clone (323 passed, 18 skipped); trace guard CLEAN |

## Decisions for the maintainer

- An empty environment variable is an error, as any unrecognised value; add `""` to a
  vocabulary to read it as false. click reads blank values as false; boolish refuses them.
- Strings are never read as numbers, in either mode and on the command line.
- One-letter answers other than `y` and `n` stay out of `MULTILINGUAL`.
- `rules` given something other than a `BoolRules` fails with Python's own
  `AttributeError`; the type hints already reject it.
- History on `main` before this branch has em-dashes in two old commits and a capitalised
  merge subject; the squash merge of this PR does not touch them.
- Source and test files stay within 200 lines (`tests/test_packaging.py`); this report,
  the GUIDE and the CHANGELOG are longer documents.

## 1.0.1

Progress:
- [x] Branch `release/1.0.1` from `main` at 91f4345, the 1.0.0 release (the PyPI 1.0.0 sdist holds the same `src` and `tests`, compared 2026-10-18)
- [x] Exact message contracts in `tests/test_contract_messages.py`
- [x] Version 1.0.1 and a dated CHANGELOG entry
- [x] Mutants B27, B29 and B33 applied one at a time, against the 1.0.0 suite and the 1.0.1 suite
- [x] Gates on a fresh clone, end-to-end module, upgrade from PyPI 1.0.0
- [x] PR #3 open, trace guard CLEAN; merge and publish left to the maintainer

A mutation sweep after the 1.0.0 release reported three mutants alive, each for want of a
contract on the text of an error message: B27 (the float preview built with `repr()`), B29
(the variable name shown with `!r`, unbounded) and B33 (the clash listing not sorted).
1.0.1 changes no library code: under `src` only the version line differs from 1.0.0. It
adds `tests/test_contract_messages.py` (15 tests), which pins each message exactly:

- a float is shown by the plain float `repr` of the value it holds: `2.5`, `-0.5`, `0.1`,
  `1e+300`, `nan` and `-inf`, and `2.5` and `inf` for a float subclass whose `__repr__`,
  `__str__`, `__format__` and `__float__` all answer something else;
- the variable named in a `getenv_bool` error is cut to its first 32 characters (names of
  32, 33 and 108 characters, read through `getenv_bool` itself) and shown by its plain text
  when it is a `str` subclass with its own `__repr__`;
- the words refused for being on both sides, and those that collide once folded, are listed
  sorted (ten of each, given in reverse order), and the command prints its listing sorted too.

### Mutants (2026-10-18)

Each mutant was applied alone to a fresh copy of a fresh clone (the edit has to match
exactly once), the whole suite run with no bytecode and no cache, and the copy thrown away;
the end-to-end module skips without `BOOLISH_E2E=1`. Run on the laptop with Python 3.14.6
and pytest 9.1.1. The 1.0.0 suite is `main` at 91f4345, the 1.0.1 suite `release/1.0.1` at
14530bc. Every test named in the last column is in `tests/test_contract_messages.py`.

| Id | Mutation | File | 1.0.0 suite | 1.0.1 suite | New tests that fail |
| --- | --- | --- | --- | --- | --- |
| B27 | float preview `repr(value)` instead of `float.__repr__(value)` | `_errors.py` | killed, 1 failed | killed, 3 failed | `test_a_float_is_shown_by_the_plain_repr_of_the_value_it_holds[sub]` and `[sub-inf]` |
| B29 | `{variable!r}` instead of `{preview(variable)}` in the environment message | `_errors.py` | killed, 1 failed | killed, 4 failed | `test_the_variable_name_is_cut_to_its_first_32_characters[33]` and `[108]`, `test_the_variable_name_is_shown_by_its_plain_text` |
| B33 | `list(words)[:10]` instead of `sorted(words)[:10]` in the clash listing | `_rules.py` | killed, 1 failed | killed, 4 failed | `test_words_on_both_sides_are_listed_sorted`, `test_words_that_collide_once_folded_are_listed_sorted`, `test_the_command_prints_the_sorted_listing` |
| B27b | extra: float preview `repr(float(value))`, so a subclass's `__float__` runs | `_errors.py` | survived, 323 passed | killed, 2 failed | `test_a_float_is_shown_by_the_plain_repr_of_the_value_it_holds[sub]` and `[sub-inf]` |
| none | the real code, before and after the mutants | | 323 passed, 18 skipped | 338 passed, 18 skipped | |

Against the whole 1.0.0 suite the three named mutants did not survive here: each made
exactly one test fail, the contract added for it after the first independent review
(edadece, `tests/test_contract_strength.py`: `test_a_float_subclass_never_runs_its_own_repr`,
`test_a_long_variable_name_is_cut_in_the_message` and
`test_a_clash_lists_the_ten_smallest_words_in_order`), and that test fails again in the
1.0.1 runs. Each message now also has exact contracts of its own, and B27b, a variant of
B27 that the 1.0.0 suite lets through, is killed. B33 leaves the listing in the set's hash
order, so it was also run under `PYTHONHASHSEED` 0 to 4 against the two contract files: the
three new tests failed under every seed.

### Gates and packaging (2026-10-18)

On a fresh clone of `release/1.0.1` at 14530bc (laptop, Python 3.14.6, ruff 0.17.1, mypy
2.4.0, pytest 9.1.1): `ruff format --check .`, `ruff check .`, `mypy --strict src` and
`pytest` (338 passed, 18 skipped, the same skips as the 1.0.0 fresh-clone runs) each exit 0,
and `mypy --strict src tests` is clean. `BOOLISH_E2E=1`: 3 passed (archives named 1.0.1,
the installed console script and `python -m boolish` answering `boolish 1.0.1`, the upgrade
from PyPI 0.1.0). The PyPI 1.0.0 wheel upgraded in place to the built 1.0.1 wheel: `pip
check` clean, the same messages before and after, `boolish 1.0.1`. The interpreter matrix
was not re-run: only the version line changed under `src`.
