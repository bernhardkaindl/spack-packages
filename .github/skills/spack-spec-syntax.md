# Spack Spec Syntax Reference for Skills and Agents

Filtered from upstream Spack documentation at
https://spack.readthedocs.io/en/latest/_sources/spec_syntax.rst.txt

Use this reference whenever a task requires reading, writing, or reviewing
Spack specs in `package.py`, `spack.yaml`, PR diffs, or skill output.

## Core Model

- A Spack spec is a constraint on a package build. It can constrain the package version,
  compiler, compiler version, variants, architecture, and dependencies.
- Specs are usually abstract when users or packages write them. Spack concretizes abstract specs
  into one exact build configuration.
- Spec syntax is recursive: a dependency after `^` or `%` is itself a spec and can have its own
  version, variants, compiler, architecture, and dependency constraints.
- Specifiers bind to the nearest package name to their left.

Example:

```spec
mpileaks@1.2:1.4 +debug ~qt target=x86_64_v3 %gcc@15 ^libelf@1.1 %clang@20
```

This means `mpileaks` at a version in the inclusive range `1.2:1.4`, `+debug`, `~qt`, target
`x86_64_v3`, built with `gcc@15`, with transitive dependency `libelf@1.1` built with `clang@20`.

## Version Specifier

Version specifiers start with `@` and are not PEP 440 specifiers. The syntax is Spack-specific.

### Ranges Are Inclusive

Spack version ranges include both endpoints:

```spec
@1.0:1.5   # all versions from 1.0 through 1.5, including 1.5.x
@:3        # all versions up to and including major version 3, including 3.x
@4.2:      # all versions greater than or equal to 4.2
```

When translating upstream half-open bounds into Spack, use the last included version series, not
sentinel patch numbers:

| Upstream constraint | Spack constraint | Notes |
|---|---|---|
| `>=3.8` | `@3.8:` | Lower-inclusive open upper bound. |
| `>=3.8,<3.11` | `@3.8:3.10` | `3.10` means the whole 3.10 series. |
| `>=1.20,<2` | `@1.20:1` | `1` means the whole major-version 1 series. |
| `<2` | `@:1` | Everything below major version 2. |
| `==3.2` | `@=3.2` | Exact version only. |

Do not write artificial bounds like `:3.10.99` or `:1.99`.

### Bare Versions Are Ranges

- `@3` is shorthand for `@3:3`, matching any version in major version 3.
- `@3.2` is a range for the `3.2` series and may match `3.2.1`, `3.2.2`, or suffix versions such
  as `3.2-custom`.
- `@=3.2` means exactly version `3.2` and does not match `3.2.1`.
- Prefer range syntax such as `@3.2` unless exact equality is required.

### Lists

A version specifier can be a comma-separated list of ranges and exact versions:

```spec
@1.0:1.5,=1.7.1
```

This matches any version in `1.0:1.5` plus exactly `1.7.1`.

### Git Versions

For packages with a `git` attribute, a version can refer to a git branch, tag, or commit:

```spec
foo@abcdef1234abcdef1234abcdef1234abcdef1234
foo@git.abcdef1234abcdef1234abcdef1234abcdef1234
foo@git.develop
foo@git.0.19
```

Spack associates git refs with a comparable Spack version. If needed, append `=<version>` to set
the version used for comparison:

```spec
foo@git.my_ref=3.2
foo@git.abcdef1234abcdef1234abcdef1234abcdef1234=develop
```

For branch-based package versions in `package.py`, prefer a `commit=` argument unless the branch is
intentionally rolling, such as `develop` or `main`. This keeps builds reproducible and usable on
air-gapped hosts.

## Variants

- Boolean variants use `+name` to enable and `~name` to disable.
- Single-valued variants use `name=value`, for example `compression=zstd`.
- Multi-valued variants use comma-separated values, for example `fabrics=verbs,ofi`.
- For multi-valued variants, `name=value1,value2` means at least those values; `name:=value1,value2`
  means exactly those values.
- Propagating variants use doubled operators: `++debug`, `--debug`, `~~debug`, or `name==value`.

## Compiler, Architecture, and Flags

- Compiler constraints use `%`, for example `%gcc@14`.
- Direct compiler dependencies can use virtual binding syntax such as `%c,cxx=clang %fortran=gcc`.
- Architecture constraints use `platform=...`, `os=...`, and `target=...`.
- Compiler flags behave like named values: `cppflags="-O3 -fPIC"`. Quote values that contain spaces.
- Propagate compiler flags with `==`, for example `cppflags=="-g"`.

## Dependencies

Spack distinguishes direct and transitive dependency constraints:

- `^dep` constrains a transitive dependency anywhere in the root package's dependency DAG.
- `%dep` constrains a direct dependency edge. It applies to the most recent transitive dependency
  to its left, or to the root package if there is no preceding `^` dependency.
- The order of transitive dependency constraints does not matter.

Example:

```spec
root %dep1 ^transitive %dep2 %dep3
```

Here `dep1` is a direct dependency of `root`, while `dep2` and `dep3` are direct dependencies of
`transitive`.

## Conditional Dependencies and `when=`

Dependency edge attributes use square brackets in CLI specs:

```spec
hdf5 ^[when=+mpi] mpich@3.1
```

In `package.py`, the same idea appears as `when=` arguments on directives such as `depends_on`,
`patch`, `conflicts`, `provides`, and `build_system`:

```python
depends_on("py-packaging@21:", type="build", when="@2025.7.0:")
patch("fix.patch", when="@:1.4")
build_system("cmake", default="cmake", when="@2:")
```

When reviewing or writing `when=` ranges:

- Interpret every `@` range using the inclusive Spack rules above.
- Gate dependencies newly introduced by a version with `when="@<introduced-version>:"` when older
  package versions remain.
- Restrict dependencies removed after a version with `when="@:<last-version-that-needed-it>"`.
- Narrow patches to the versions they are known to apply to; do not leave patches ungated if newer
  versions may not need or accept them.
- Do not add speculative upper bounds. Add an upper bound only when upstream declares an
  incompatibility, a dependency was removed, or a patch truly stops applying.
