Name: libfabric
Version: 1.8.0
Release: 1.1%{?dist}
Summary: User-space RDMA Fabric Interfaces
%if 0%{?suse_version} >= 1315
License: GPL-2.0-only OR BSD-2-Clause
Group: Development/Libraries/C and C++    
%else
Group: System Environment/Libraries
License: GPLv2 or BSD
%endif
Url: https://www.github.com/ofiwg/libfabric
Source: https://github.com/ofiwg/%{name}/archive/v%{version}.tar.gz

%if 0%{?rhel} >= 7
BuildRequires: librdmacm-devel
BuildRequires: libibverbs-devel >= 1.2.0
BuildRequires: libnl3-devel
# needed for psm2_am_register_handlers_2@PSM2_1.0
BuildRequires: libpsm2-devel >= 10.3.58
%else
%if 0%{?suse_version} >= 1315
BuildRequires: libibverbs-devel >= 1.2.0
BuildRequires: rdma-core-devel
BuildRequires: libnl3-devel
BuildRequires: fdupes
%define lib_major 1
%endif
%endif

# infinipath-psm-devel only available for x86_64
%ifarch x86_64
BuildRequires: infinipath-psm-devel
%if 0%{?suse_version} >= 1315 || 0%{?rhel} >= 7
BuildRequires: libpsm2-devel >= 10.3.58
%endif
%endif
# valgrind is unavailable for s390
%ifnarch s390
BuildRequires: valgrind-devel
%endif

# to be able to generate configure if not present
BuildRequires: autoconf, automake, libtool

%ifarch x86_64
%if 0%{?suse_version} >= 01315 || 0%{?rhel} >= 7
%global configopts --enable-sockets --enable-verbs --enable-usnic --disable-static --enable-psm --enable-psm2
%else
%global configopts --enable-sockets --enable-verbs --enable-usnic --disable-static
%endif
%else
%global configopts --enable-sockets --enable-verbs --enable-usnic --disable-static
%endif

%description
libfabric provides a user-space API to access high-performance fabric
services, such as RDMA.

%if 0%{?suse_version} >= 01315
%package       -n %{name}%{?lib_major}
Summary:        User-space RDMA fabric interfaces
Group:          System/Libraries

%description -n %{name}%{?lib_major}
libfabric provides a user-space API to access high-performance fabric
services, such as RDMA. This package contains the runtime library.

%endif

%package devel
Summary: Development files for the libfabric library
%if 0%{?suse_version} >= 01315
Group: Development/Libraries/C and C++
%else
Group: System Environment/Libraries
%endif
Requires: %{name}%{?lib_major}%{?_isa} = %{version}-%{release}

%description devel
%if 0%{?suse_version} >= 01315
libfabric provides a user-space API to access high-performance fabric
services, such as RDMA. This package contains the development files.    
%else
Development files for the libfabric library.
%endif

%prep
%setup -q

%build
if [ ! -f configure ]; then
    ./autogen.sh
fi
# defaults: with-dlopen can be over-rode:
%configure %{?_without_dlopen} %{configopts} \
%ifnarch s390
	--with-valgrind
%endif
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags} V=1

%install
%make_install
# remove unpackaged files from the buildroot
rm -f %{buildroot}%{_libdir}/*.la
%if 0%{?suse_version} >= 01315
%fdupes %{buildroot}/%{_prefix}

%post -n libfabric%{lib_major} -p /sbin/ldconfig
%postun -n libfabric%{lib_major} -p /sbin/ldconfig
%else

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig
%endif

%if 0%{?suse_version} >= 01315
%files
%defattr(-,root,root,-)
%{_bindir}/*
%{_mandir}/man1/*
%doc NEWS.md
%license COPYING
%endif

%files -n libfabric%{?lib_major}
%if 0%{?suse_version} >= 01315
%defattr(-,root,root)
%endif    
%{_libdir}/libfabric.so.*
%if 0%{?rhel} >= 7
%{_bindir}/fi_info
%{_bindir}/fi_pingpong
%{_bindir}/fi_strerror
%{_libdir}/pkgconfig/%{name}.pc
%{_mandir}/man1/*
%endif
%license COPYING
%doc AUTHORS README

%files devel
%if 0%{?suse_version} >= 01315
%defattr(-,root,root)
%{_libdir}/pkgconfig/%{name}.pc

%endif
%{_libdir}/libfabric.so
%{_includedir}/*
%{_mandir}/man3/*
%{_mandir}/man7/*

%changelog
* Fri Aug 09 2019 John E. Malmberg <john.e.malmberg@intel.com> - 1.8.0-1.1
- Fixes to use suse build utility for building.

* Thu Jul 25 2019 Alexander A. Oganeozv <alexnader.a.oganezov@intel.com> - 1.8.0
- Update to 1.8.0

* Wed Jun 26 2019 Brian J. Murrell <brian.murrell@intel.com> - 1.7.1rc1-4
- Add BuildRequires: libpsm2-devel >= 10.3.58
  - needed for psm2_am_register_handlers_2@PSM2_1.0

* Tue May 14 2019 Brian J. Murrell <brian.murrell@intel.com> - 1.7.1rc1-3
- Fix SLES 12.3 OS conditionals >= 1315

* Wed May 01 2019 Brian J. Murrell <brian.murrell@intel.com> - 1.7.1rc1-2
- Disable psm2 on SLES 12.3 as the psm2 library there is too old

* Tue Mar 19 2019 Brian J. Murrell <brian.murrell@intel.com> - 1.7.1rc1-1
- Update to 1.7.1 RC1

* Mon Mar 11 2019 Brian J. Murrell <brian.murrell@intel.com> - 1.7.0rc3-1
- Rebase to latest release 1.7.0rc3

* Wed Aug 15 2018 Brian J. Murrell <brian.murrell@intel.com> - 1.6.0-1
- Rebase to latest release 1.6.0
- Remove obsolete patch
- Strip out local libtool Rpathing per
  https://fedoraproject.org/wiki/RPath_Packaging_Draft#Removing_Rpath

* Wed Jan 10 2018 Honggang Li <honli@redhat.com> - 1.5.3-1
- Rebase to latest release 1.5.3
- Resolves: bz1533293

* Thu Jan  4 2018 Honggang Li <honli@redhat.com> - 1.5.1-3
- Add support of different CQ formats for the verbs/RDM
- Resolves: bz1530715

* Fri Oct 20 2017 Honggang Li <honli@redhat.com> - 1.5.1-2
- Fix PPC32 compiling issue
- Resolves: bz1504395

* Tue Oct 17 2017 Honggang Li <honli@redhat.com> - 1.5.1-1
- Rebase to v1.5.1
- Resolves: bz1452791

* Tue May 16 2017 Honggang Li <honli@redhat.com> - 1.4.2-1
- Update to upstream v1.4.2 release
- Related: bz1451100

* Wed Mar 01 2017 Jarod Wilson <jarod@redhat.com> - 1.4.1-1
- Update to upstream v1.4.1 release
- Related: bz1382827

* Mon May 30 2016 Honggang Li <honli@redhat.com> - 1.3.0-3
- Rebuild against latest infinipath-psm.
- Related: bz1280143

* Mon May 30 2016 Honggang Li <honli@redhat.com> - 1.3.0-2
- Rebuild libfabric to support Intel OPA PSM2.
- Related: bz1280143

* Wed May  4 2016 Honggang Li <honli@redhat.com> - 1.3.0-1
- Update to latest upstream release
- Related: bz1280143

* Wed Sep 30 2015 Doug Ledford <dledford@redhat.com> - 1.1.0-2
- Rebuild against libnl3 now that the UD RoCE bug is fixed
- Related: bz1261028

* Fri Aug 14 2015 Honggang Li <honli@redhat.com> - 1.1.0-1
- Rebase to upstream 1.1.0
- Resolves: bz1253381

* Fri Aug 07 2015 Michal Schmidt <mschmidt@redhat.com> - 1.1.0-0.2.rc4
- Packaging Guidelines conformance fixes and spec file cleanups
- Related: bz1235266

* Thu Aug  6 2015 Honggang Li <honli@redhat.com> - 1.1.0-0.1.rc4
- fix N-V-R issue and disable static library
- Related: bz1235266

* Tue Aug  4 2015 Honggang Li <honli@redhat.com> - 1.1.0rc4
- Initial build for RHEL-7.2
- Related: bz1235266

* Fri Jun 26 2015 Open Fabrics Interfaces Working Group <ofiwg@lists.openfabrics.org> 1.1.0rc1
- Release 1.1.0rc1

* Sun May 3 2015 Open Fabrics Interfaces Working Group <ofiwg@lists.openfabrics.org> 1.0.0
- Release 1.0.0
