%define staticdevelname %mklibname %{name} -d -s

Summary:	Advanced IP routing and network device configuration tools
Name:		iproute2
Version:	2.6.28
Release:	%mkrel 1
License:	GPLv2+
Group:		Networking/Other
Url:		http://www.linuxfoundation.org/en/Net:Iproute2
Source0:	http://devresources.linux-foundation.org/dev/iproute2/download/%{name}-%{version}.tar.bz2
Source2:	iproute2-man8.tar.bz2
# RH patches
# rediffed from Cross LFS: http://ftp.osuosl.org/pub/clfs/clfs-packages/svn/
# (tpg) partially upstream accepted
Patch8:		iproute2-2.6.28-libdir.patch
# MDK patches
Patch100:	iproute2-def-echo.patch
Patch102:	iproute2-2.4.7-bashfix.patch
Patch106:	iproute2-2.6.X-ss040702-build-fix.patch
Patch107:	iproute2-2.6.28-segfault.patch
Patch108:	iproute2-2.6.28-format_not_a_string_literal_and_no_format_arguments.patch
BuildRequires:	bison
BuildRequires:	db4-devel
BuildRequires:	flex
BuildRequires:	kernel-source
BuildRequires:	linuxdoc-tools
BuildRequires:	linux-atm-devel
Requires:	iputils
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The iproute package contains networking utilities (ip, tc and rtmon, for
example) which are designed to use the advanced networking capabilities of the
Linux 2.2.x kernels and later,  such as policy routing, fast NAT and packet
scheduling.

%package -n %{staticdevelname}
Summary:	Development files for iproute2
Group:		Development/C
Provides:	iproute2-devel = %{version}-%{release}

%description -n	%{staticdevelname}
The iproute package contains networking utilities (ip, tc and rtmon, for
example) which are designed to use the advanced networking capabilities of the
Linux 2.2.x kernels and later,  such as policy routing, fast NAT and packet
scheduling.

This package contains development files for iproute2.

%package doc
Summary:	Documentation for Advanced IP routing and network device configuration tools
Group:		Networking/Other

%description doc
Documentation for iproute2.

%prep

%setup -q
%patch8 -p1 -b .libdir

%patch100 -p0
%patch102 -p1 -b .bashfix
%patch106 -p1 -b .build
%patch107 -p1 -b .segv
%patch108 -p1

%build
%serverbuild
%setup_compile_flags
export CCOPTS="%{optflags} -ggdb"
export SBINDIR=/sbin
export LIBDIR=/%{_lib}
export VARLIB=/var/lib
export INCLUDEDIR=%{_includedir}

# (tpg) don't use macro here
./configure

%make KERNEL_INCLUDE=/usr/src/linux/include LIBDIR=/%{_lib}
%make -C doc

%install
rm -rf %{buildroot}

%makeinstall_std SBINDIR=/sbin LIBDIR=/%{_lib} VARLIB=/var/lib MANDIR=%{_mandir} DOCDIR=%{_docdir}/%{name}-%{version}

mv %{buildroot}/sbin/arpd %{buildroot}/sbin/iproute-arpd
tar -jxf %{SOURCE2} -C %{buildroot}%{_mandir}

# development files
install -d %{buildroot}%{_includedir}
install -m0644 lib/libnetlink.a %{buildroot}/%{_lib}/
install -m0644 include/libnetlink.h %{buildroot}%{_includedir}/

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%dir %{_sysconfdir}/iproute2
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/iproute2/*
/sbin/*
/%{_lib}/tc
%{_mandir}/man8/*
%{_mandir}/man3/*

%files -n %{staticdevelname}
%defattr (-,root,root)
%{_includedir}/*.h
/%{_lib}/*.a

%files doc
%defattr (-,root,root)
%doc README README.iproute2+tc RELNOTES README.decnet
%doc doc/*.dvi doc/*.ps doc/Plan
%doc %{_docdir}/%{name}-%{version}/*.sgml
%doc %{_docdir}/%{name}-%{version}/*.tex
%doc %{_docdir}/%{name}-%{version}/examples
