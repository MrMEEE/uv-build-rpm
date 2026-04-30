## START: Set by rpmautospec
## (rpmautospec version 0.8.2)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 3;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%bcond check 1

Name:           python-uv-build
Version:        0.8.11
Release:        %autorelease
Summary:        The uv build backend

# The license of the uv project is (MIT OR Apache-2.0), except:
#
# Apache-2.0 OR BSD-2-Clause:
#   - crates/uv-pep440/ is vendored and forked from crate(pep440_rs)
#   - crates/uv-pep508/ is vendored and forked from crate(pep508_rs)
#
# Rust crates compiled into the executable contribute additional license terms.
# To obtain the following list of licenses, build the package and note the
# output of %%{cargo_license_summary}. This should automatically include the
# licenses of the following bundled forks:
#   - pubgrub/version-ranges, Source200, is MPL-2.0.
#   - reqwest-middleware/reqwest-retry, Source300, is (MIT OR Apache-2.0).
#
# (Apache-2.0 OR MIT) AND BSD-3-Clause
# (MIT OR Apache-2.0) AND Unicode-3.0
# (MIT OR Apache-2.0) AND Unicode-DFS-2016
# 0BSD
# 0BSD OR MIT OR Apache-2.0
# Apache-2.0
# Apache-2.0 OR BSD-2-Clause
# Apache-2.0 OR BSL-1.0
# Apache-2.0 OR MIT
# Apache-2.0 OR MIT OR Zlib
# Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT
# BSD-2-Clause OR Apache-2.0 OR MIT
# MIT
# MIT OR Apache-2.0
# MIT OR Zlib OR Apache-2.0
# MIT-0 OR Apache-2.0
# MPL-2.0
# Unicode-3.0
# Unlicense OR MIT
# Zlib
License:        %{shrink:
                (Apache-2.0 OR MIT) AND
                (Apache-2.0 OR BSD-2-Clause) AND
                MPL-2.0
                }
%global extra_crate_licenses %{shrink:
                0BSD AND
                (0BSD OR MIT OR Apache-2.0) AND
                Apache-2.0 AND
                (Apache-2.0 OR BSD-2-Clause OR MIT) AND
                (Apache-2.0 OR BSL-1.0) AND
                (Apache-2.0 OR MIT OR Zlib) AND
                (Apache-2.0 OR MIT-0) AND
                (Apache-2.0 OR Apache-2.0 WITH LLVM-exception OR MIT) AND
                BSD-3-Clause AND
                MIT AND
                (MIT OR Unlicense) AND
                Unicode-3.0 AND
                Unicode-DFS-2016 AND
                Zlib
                }
URL:            https://pypi.org/project/uv-build
Source:         %{pypi_source uv_build}

# This package is ultimately built from the same source tree as uv, i.e.
# https://github.com/astral-sh/uv, and belongs to the same cargo workspace.
#
# The PyPI sdist includes a small subset of the same workspace crates as uv.
# (Note that these are not published on crates.io, and are neither intended for
# separate distribution nor suitable for separate packaging.)
#
# We choose not to build uv-build from the uv source package because this spec
# file can be much simpler than the one for uv, because the separation helps to
# keep track of which patches, licenses, additional sources, etc. apply to
# uv-build, and because – while it normally makes sense to synchronize updates
# of this package with uv updates – there will likely be times when we want to
# keep updating uv (primarily a developer tool) while holding uv-build
# (primarily used for building packages) at an older version for compatibility.

# For the foreseeable future, uv must use a fork of pubgrub (and the
# version-ranges crate, which belongs to the same project), as explained in:
#   Plans for eventually using published pubgrub?
#   https://github.com/astral-sh/uv/issues/3794
# We therefore bundle the fork as prescribed in
#   https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/#_replacing_git_dependencies
# Note that uv-build currently only uses version-ranges, not pubgrub.
%global pubgrub_git https://github.com/astral-sh/pubgrub
%global pubgrub_rev 06ec5a5f59ffaeb6cf5079c6cb184467da06c9db
%global pubgrub_snapdate 20250523
%global version_ranges_baseversion 0.1.1
Source200:      %{pubgrub_git}/archive/%{pubgrub_rev}/pubgrub-%{pubgrub_rev}.tar.gz

# Until “Report retry count on Ok results,”
# https://github.com/TrueLayer/reqwest-middleware/pull/235, is reviewed,
# merged, and released, uv must use a fork of reqwest-middleware/reqwest-retry
# to support the changes in “Show retries for HTTP status code errors,”
# https://github.com/astral-sh/uv/pull/13897. We therefore bundle the fork as
# prescribed in
#   https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/#_replacing_git_dependencies
%global reqwest_middleware_git https://github.com/astral-sh/reqwest-middleware
%global reqwest_middleware_rev ad8b9d332d1773fde8b4cd008486de5973e0a3f8
%global reqwest_middleware_snapdate 20250607
%global reqwest_retry_baseversion 0.7.0
Source300:      %{reqwest_middleware_git}/archive/%{reqwest_middleware_rev}/reqwest-middleware-%{reqwest_middleware_rev}.tar.gz


# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
# Also, there are a couple of test failures on 32-bit platforms.
ExcludeArch:   %{ix86}

BuildRequires:  tomcli
BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  rust2rpm-helper

%global common_description %{expand:
This package is a slimmed down version of uv containing only the build
backend.}

%description
%{common_description}


%package -n     python3-uv-build
Summary:        %{summary}
License:        %{license} AND %{extra_crate_licenses}
# LICENSE.dependencies contains a full license breakdown

# This is a fork of pubgrub/version-ranges; see the notes about Source200.
%global pubgrub_snapinfo %{pubgrub_snapdate}git%{sub %{pubgrub_rev} 1 7}
%global version_ranges_version %{version_ranges_baseversion}^%{pubgrub_snapinfo}
Provides:       bundled(crate(version-ranges)) = %{version_ranges_version}
# This is a fork of reqwest-middleware/reqwest-retry; see the notes about
# Source300.
%global reqwest_middleware_snapinfo %{reqwest_middleware_snapdate}git%{sub %{reqwest_middleware_rev} 1 7}
%global reqwest_retry_version %{reqwest_retry_baseversion}^%{reqwest_middleware_snapinfo}
Provides:       bundled(crate(reqwest-retry)) = %{reqwest_retry_version}

# In https://github.com/astral-sh/uv/issues/5588#issuecomment-2257823242,
# upstream writes “These have diverged significantly and the upstream versions
# are only passively maintained, uv requires these custom versions and can't
# use a system copy.”
#
# crates/uv-pep440/
# Version number from Cargo.toml:
Provides:       bundled(crate(pep440_rs)) = 0.7.0
# crates/uv-pep508/
# Cargo.toml has 0.6.0, but Changelog.md shows 0.7.0, and the source reflects
# the changes for 0.7.0:
Provides:       bundled(crate(pep508_rs)) = 0.7.0

%description -n python3-uv-build
%{common_description}


%prep
%autosetup -n uv_build-%{version} -N
%autopatch -p1 -M99

# Usage: git2path SELECTOR PATH
# Replace a git dependency with a path dependency in Cargo.toml
git2path() {
  tomcli set Cargo.toml del "${1}.git"
  tomcli set Cargo.toml del "${1}.rev"
  tomcli set Cargo.toml str "${1}.path" "${2}"
}

# See comments above Source200:
%setup -q -T -D -b 200 -n uv_build-%{version}
pushd '../pubgrub-%{pubgrub_rev}/'
%autopatch -p1 -m200 -M299
popd
ln -s '../../pubgrub-%{pubgrub_rev}/version-ranges' crates/version-ranges
# Convert the symlinked LICENSE in version-ranges to a regular file, since we
# will be removing top-level files from pubgrub.
rm -v crates/version-ranges/LICENSE
cp -p '../pubgrub-%{pubgrub_rev}/LICENSE' crates/version-ranges/
# Prove that we do not use the pubgrub crate by removing everything except the
# version-ranges subdirectory.
find '../pubgrub-%{pubgrub_rev}/' -mindepth 1 -maxdepth 1 \
    ! -name 'version-ranges' -execdir rm -rv '{}' '+'
# Note that install does always dereference symlinks, which is what we want:
install -t LICENSE.bundled/version-ranges -D -p -m 0644 \
    crates/version-ranges/LICENSE
git2path workspace.dependencies.version-ranges crates/version-ranges

# See comments above Source300:
%setup -q -T -D -b 300 -n uv_build-%{version}
pushd '../reqwest-middleware-%{reqwest_middleware_rev}/reqwest-middleware'
%autopatch -p1 -m300 -M399
popd
# Upstream has only modified reqwest-retry, so we may as well use the system
# copy of reqwest-middleware.
rm -rv '../reqwest-middleware-%{reqwest_middleware_rev}/reqwest-middleware'
tomcli set Cargo.toml del 'workspace.dependencies.reqwest-middleware.git'
tomcli set Cargo.toml del 'workspace.dependencies.reqwest-middleware.rev'
tomcli set Cargo.toml str 'workspace.dependencies.reqwest-middleware.version' \
    '0.4.2'
tomcli set Cargo.toml del patch.crates-io.reqwest-middleware
ln -s '../../reqwest-middleware-%{reqwest_middleware_rev}/reqwest-retry' \
    crates/reqwest-retry
git2path workspace.dependencies.reqwest-retry crates/reqwest-retry
tomcli set Cargo.toml del patch.crates-io.reqwest-retry
tomcli set crates/reqwest-retry/Cargo.toml del \
    'dependencies.reqwest-middleware.path'
install -t LICENSE.bundled/reqwest-retry -D -p -m 0644 \
    crates/reqwest-retry/LICENSE*
# We do not need the reqwest-tracing crate.
rm -rv '../reqwest-middleware-%{reqwest_middleware_rev}/reqwest-tracing'

# Collect license files of vendored dependencies in the main source archive
install -t LICENSE.bundled/pep440_rs -D -p -m 0644 crates/uv-pep440/License-*
install -t LICENSE.bundled/pep508_rs -D -p -m 0644 crates/uv-pep508/License-*

# Patch out foreign (e.g. Windows-only) dependencies.
find -L . -type f -name Cargo.toml -print \
    -execdir rust2rpm-helper strip-foreign -o '{}' '{}' ';'

# Do not strip the compiled executable; we need useful debuginfo. Upstream set
# this intentionally, so this change makes sense to keep downstream-only.
tomcli set pyproject.toml false tool.maturin.strip
tomcli set Cargo.toml false profile.release.strip

%cargo_prep


%generate_buildrequires -p
# For unclear reasons, maturin checks for all crate dependencies when it is
# invoked as part of %%pyproject_buildrequires – including those corresponding
# to optional features.
#
# Since maturin always checks for dev-dependencies, we need -t so that they are
# generated even when the “check” bcond is disabled.
%cargo_generate_buildrequires -a -t


%build -p
%cargo_license_summary
%{cargo_license} > LICENSE.dependencies


%check -a
%if %{with check}
# These tests require files from scripts/packages/built-by-uv/, which are not
# included in the sdist.
skip="${skip-} --skip tests::built_by_uv_building"
skip="${skip-} --skip wheel::test::test_prepare_metadata"

%cargo_test -- -- --exact ${skip-}
%endif


%files -n python3-uv-build -f %{pyproject_files}
# The other license files (LICENSE-APACHE, LICENSE-MIT, and
# LICENSE.dependencies) are already handled in the .dist-info directory.
%license LICENSE.bundled/
%doc README.md

%{_bindir}/uv-build
# Output of uv-build --help:
#   uv_build contains only the PEP 517 build backend for uv and can't be used
#   on the CLI. Use `uv build` or another build frontend instead.
# Therefore, it does not make sense to package a man page.


%changelog
## START: Generated by rpmautospec
* Fri Sep 19 2025 Python Maint <python-maint@redhat.com> - 0.8.11-3
- Rebuilt for Python 3.14.0rc3 bytecode

* Tue Sep 02 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.11-2
- Rebuilt with rust-tracing-subscriber-0.3.20
- Fixes CVE-2025-58160: fixes RHBZ#2392055, fixes RHBZ#2392012, fixes
  RHBZ#2391975

* Sat Aug 16 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.11-1
- Update to 0.8.11 (close RHBZ#2388438)

* Sat Aug 16 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.10-1
- Update to 0.8.10

* Fri Aug 15 2025 Python Maint <python-maint@redhat.com> - 0.8.9-2
- Rebuilt for Python 3.14.0rc2 bytecode

* Wed Aug 13 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.9-1
- Update to 0.8.9 (close RHBZ#2387765)

* Sat Aug 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.8-1
- Update to 0.8.8 (close RHBZ#2387092)

* Sat Aug 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.7-1
- Update to 0.8.7

* Sat Aug 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.6-1
- Update to 0.8.6

* Wed Aug 06 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.5-1
- Update to 0.8.5 (close RHBZ#2386645)

* Thu Jul 31 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.4-1
- Update to 0.8.4 (close RHBZ#2381737)

* Thu Jul 31 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.3-1
- Update to 0.8.3

* Tue Jul 29 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.2-1
- Update to 0.8.2

* Tue Jul 29 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.1-1
- Update to 0.8.1

* Tue Jul 29 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.0-1
- Update to 0.8.0

* Fri Jul 25 2025 Fedora Release Engineering <releng@fedoraproject.org> - 0.7.22-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Sat Jul 19 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.22-1
- Update to 0.7.22

* Tue Jul 15 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.21-1
- Update to 0.7.21 (close RHBZ#2379123)

* Thu Jul 10 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.20-1
- Update to 0.7.20 (close RHBZ#2379145)

* Tue Jul 08 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.19-1
- Update to 0.7.19 (close RHBZ#2375432)

* Tue Jul 08 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.18-1
- Update to 0.7.18

* Tue Jul 08 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.17-1
- Update to 0.7.17

* Sat Jun 28 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.16-1
- Update to 0.7.16 (close RHBZ#2374368)

* Sat Jun 28 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.15-1
- Update to 0.7.15

* Thu Jun 26 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.14-1
- Update to 0.7.14

* Thu Jun 26 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.13-2
- Correctly patch out foreign deps. in bundled crates

* Fri Jun 13 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.13-1
- Update to 0.7.13 (close RHBZ#2372600)

* Mon Jun 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.12-1
- Update to 0.7.12 (close RHBZ#2370052)

* Mon Jun 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.11-1
- Update to 0.7.11

* Mon Jun 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.10-1
- Update to 0.7.10

* Tue Jun 03 2025 Python Maint <python-maint@redhat.com> - 0.7.9-2
- Rebuilt for Python 3.14

* Sat May 31 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.9-1
- Update to 0.7.9 (close RHBZ#2369520)

* Sun May 25 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.8-1
- Update to 0.7.8 (close RHBZ#2368082)

* Tue May 20 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.6-1
- Update to 0.7.6 (close RHBZ#2367412)

* Sat May 17 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.5-1
- Update to 0.7.5 (close RHBZ#2362369)

* Sat May 17 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.4-1
- Update to 0.7.4

* Fri May 16 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.3-1
- Update to 0.7.3

* Fri May 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.2-1
- Update to 0.7.2

* Fri May 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.1-1
- Update to 0.7.1

* Fri May 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.7.0-1
- Update to 0.7.0

* Fri May 09 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.17-2
- F41+: Use the provisional pyproject declarative buildsystem

* Mon May 05 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.17-1
- Update to 0.6.17

* Fri Apr 25 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.16-3
- Fix a typo in the LICENSE expression (missing AND)

* Fri Apr 25 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.16-2
- Update ron to 0.10

* Tue Apr 22 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.16-1
- Update to 0.6.16 (close RHBZ#2361554)
- Update the License expression, primarily due to rust-idna 1.x

* Sat Apr 12 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.14-2
- Patch bundled pubgrub/version-ranges fork for ron 0.9.0 final

* Thu Apr 10 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.14-1
- Update to 0.6.14 (close RHBZ#2358749)

* Tue Apr 08 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.13-1
- Update to 0.6.13 (close RHBZ#2358054)

* Sat Apr 05 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.12-2
- Let LICENSE.dependencies be installed in the .dist-info

* Fri Apr 04 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.6.12-1
- Initial package (close RHBZ#2357473)
## END: Generated by rpmautospec
