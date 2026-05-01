## START: Set by rpmautospec
## (rpmautospec version 0.8.4)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 1;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%bcond check 1

Name:           python-uv-build
Version:        0.11.7
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
# output of %%{cargo_license_summary}.
#
# (Apache-2.0 OR MIT) AND BSD-3-Clause
# (MIT OR Apache-2.0) AND Apache-2.0 AND CC0-1.0
# (MIT OR Apache-2.0) AND Unicode-3.0
# (MIT OR Apache-2.0) AND Unicode-DFS-2016
# 0BSD
# Apache-2.0
# Apache-2.0 OR BSD-2-Clause
# Apache-2.0 OR BSL-1.0
# Apache-2.0 OR MIT
# Apache-2.0 OR MIT OR Zlib
# Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT
# MIT
# MIT OR Apache-2.0
# MIT-0 OR Apache-2.0
# MPL-2.0
# Unicode-3.0
# Unlicense OR MIT
# Zlib
# bzip2-1.0.6
License:        %{shrink:
                (Apache-2.0 OR MIT) AND
                (Apache-2.0 OR BSD-2-Clause) AND
                MPL-2.0
                }
%global extra_crate_licenses %{shrink:
                0BSD AND
                Apache-2.0 AND
                (Apache-2.0 OR BSL-1.0) AND
                (Apache-2.0 OR MIT OR Zlib) AND
                (Apache-2.0 OR MIT-0) AND
                (Apache-2.0 OR Apache-2.0 WITH LLVM-exception OR MIT) AND
                BSD-3-Clause AND
                CC0-1.0 AND
                MIT AND
                (MIT OR Unlicense) AND
                Unicode-3.0 AND
                Unicode-DFS-2016 AND
                Zlib AND
                bzip2-1.0.6
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

#BuildSystem:            pyproject
#BuildOption(install):   -l uv_build

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
%autosetup -n uv_build-%{version} -p1
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o rustup.sh
sh rustup.sh -y

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

# Do not request static linking of anything (particularly, liblzma)
tomcli set Cargo.toml lists delitem \
    workspace.dependencies.xz2.features 'static'

# We retain the following example even when there are currently no dependencies
# that need to be adjusted.
#
# # foocrate
# #   wanted: 0.2.0
# #   currently packaged: 0.1.2
# #   https://bugzilla.redhat.com/show_bug.cgi?id=1234567
# tomcli set Cargo.toml str workspace.dependencies.foocrate.version 0.1.2

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
* Thu Apr 16 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.11.7-1
- Update to 0.11.7 (close RHBZ#2458852)

* Thu Apr 09 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.11.6-1
- Update to 0.11.6 (close RHBZ#2456895)

* Thu Apr 09 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.11.5-1
- Update to 0.11.5 (close RHBZ#2456733)

* Wed Apr 08 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.11.4-1
- Update to 0.11.4 (close RHBZ#2454125)

* Fri Mar 27 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.11.2-1
- Update to 0.11.2 (close RHBZ#2450541)

* Fri Mar 20 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.12-1
- Update to 0.10.12 (close RHBZ#2449338)

* Tue Mar 17 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.11-1
- Update to 0.10.11 (close RHBZ#2448298)

* Sun Mar 15 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.10-1
- Update to 0.10.10 (close RHBZ#2447539)

* Sun Mar 08 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.9-1
- Update to 0.10.9 (close RHBZ#2445333)

* Wed Mar 04 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.8-1
- Update to 0.10.8 (close RHBZ#2444234)

* Fri Feb 27 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.7-1
- Update to 0.10.7 (close RHBZ#2443311)

* Wed Feb 25 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.6-1
- Update to 0.10.6 (close RHBZ#2442128)

* Wed Feb 25 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.5-1
- Update to 0.10.5

* Wed Feb 18 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.4-1
- Update to 0.10.4 (close RHBZ#2440502)

* Mon Feb 16 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.3-1
- Update to 0.10.3 (close RHBZ#2440200)

* Tue Feb 10 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.2-1
- Update to 0.10.2

* Tue Feb 10 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.1-1
- Update to 0.10.1 (close RHBZ#2438446)

* Fri Feb 06 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.10.0-1
- Update to 0.10.0 (close RHBZ#2437187)

* Thu Feb 05 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.30-1
- Update to 0.9.30 (close RHBZ#2436958)

* Tue Feb 03 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.29-1
- Update to 0.9.29 (close RHBZ#2436549)

* Thu Jan 29 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.28-1
- Update to 0.9.28 (close RHBZ#2433122)

* Thu Jan 29 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.27-1
- Update to version 0.9.27

* Sat Jan 17 2026 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.26-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_44_Mass_Rebuild

* Thu Jan 15 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.26-1
- Update to 0.9.26 (close RHBZ#2428321)

* Tue Jan 06 2026 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.22-1
- Update to 0.9.22 (close RHBZ#2427389)

* Tue Dec 30 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.21-1
- Update to 0.9.21 (close RHBZ#2425889)

* Tue Dec 30 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.20-1
- Update to 0.9.20 (close RHBZ#2425889)

* Tue Dec 16 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.18-1
- Update to 0.9.18 (close RHBZ#2422785)

* Sun Dec 14 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.17-2
- Update spdx to 0.13

* Thu Dec 11 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.17-1
- Update to 0.9.17

* Thu Dec 11 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.16-1
- Update to 0.9.16

* Thu Dec 11 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.15-1
- Update to 0.9.15

* Thu Dec 11 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.14-1
- Update to 0.9.14

* Thu Dec 11 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.13-1
- Update to 0.9.13

* Thu Dec 11 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.12-1
- Update to 0.9.12

* Thu Dec 11 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.11-1
- Update to 0.9.11

* Thu Dec 11 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.10-1
- Update to 0.9.10

* Sat Nov 15 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.9-1
- Update to 0.9.9 (close RHBZ#2414659)

* Fri Nov 07 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.8-1
- Update to 0.9.8 (close RHBZ#2413460)

* Sun Nov 02 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.7-2
- Allow spdx 0.12

* Fri Oct 31 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.7-1
- Update to 0.9.7 (close RHBZ#2408519)

* Wed Oct 29 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.6-1
- Update to 0.9.6 (close RHBZ#2407236)

* Fri Oct 24 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.5-1
- Update to 0.9.5 (close RHBZ#2402881)

* Fri Oct 24 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.4-1
- Update to 0.9.4

* Thu Oct 23 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.3-1
- Update to 0.9.3

* Thu Oct 23 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.2-1
- Update to 0.9.2

* Thu Oct 23 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.1-1
- Update to 0.9.1

* Thu Oct 23 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.9.0-1
- Update to 0.9.0

* Wed Oct 22 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.24-1
- Update to 0.8.24

* Wed Oct 22 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.23-1
- Update to 0.8.23

* Wed Oct 22 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.22-1
- Update to 0.8.22

* Wed Oct 22 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.21-1
- Update to 0.8.21

* Mon Sep 29 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.20-1
- Update to 0.8.20 (close RHBZ#2389312)

* Mon Sep 29 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.19-1
- Update to 0.8.19

* Mon Sep 29 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.18-1
- Update to 0.8.18

* Sun Sep 28 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.17-1
- Update to 0.8.17

* Sun Sep 28 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.16-1
- Update to 0.8.16

* Sun Sep 28 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.15-1
- Update to 0.8.15

* Sun Sep 28 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.14-1
- Update to 0.8.14

* Sun Sep 28 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.13-1
- Update to 0.8.13

* Sun Sep 28 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.12-1
- Update to 0.8.12

* Sun Sep 28 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 0.8.11-4
- Use the bundled reqwest-middleware, too

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
