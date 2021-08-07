
# CHANGELOG

Suggested pull request and commit types:
- improve: Improved an existing feature
- feature: Added a new feature
- fix: Fixed a bug
- doc: Added, updated, or fixed documentation
- deprecated: Deprecated a feature or function
- breaking: Made a breaking change

Template commit message:

    <type>(<module>) <message>

    <longer message>

Example commit message:

    fix(vasp) update test structure to use 'lattice_vectors'

    The structure.json test data for the vasp module needed to be
    updated to use 'lattice_vectors' instead of 'lattice'.

# 1.2.1 (2021-08-07)

| Type | Commit | Message |
|------|--------|---------|
| fix(calc) | [8be6a33](https://github.com/prisms-center/CASMpython/commit/8be6a332d383c55ffdd5657c23e00104c964120b) | Fix vaspwrapper interactions with prisms_jobs | fix(calc) | [a4e0fa6](https://github.com/prisms-center/CASMpython/commit/a4e0fa69c6ef270db650fd4e8661268ce5ff43d2) | Write/read structure file instead of POS for vasp setup |
| fix(calc) | [ed9fcf8](https://github.com/prisms-center/CASMpython/commit/ed9fcf8d117511865f2f08d71983dde2ca8a3196) | Fix bugs causing `calc --setup` to fail  |


# 1.2.0 (2021-08-06)

| Type | Commit | Message |
|------|--------|---------|
| breaking | [013de5f](https://github.com/prisms-center/CASMpython/commit/e2b1cc910d9c1293088cef5c32c5c7d7e8184065) | Only support CASM 1.2.0 structure format: atom/mol/global "_properties" instead of "_dofs" suffix, "lattice_vectors" instead of "lattice"; prim JSON format using species "properties" instead of "attributes" |
| feature(convert) | [013de5f](https://github.com/prisms-center/CASMpython/commit/013de5fe5bb218d9959172d915377455973b274d) | New `casm convert` method uses [ASE](https://wiki.fysik.dtu.dk/ase/) to convert to/from CASM structure JSON format and other crystal structure formats. |
