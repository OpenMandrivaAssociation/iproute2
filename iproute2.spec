%define build_doc 0
%define staticdevelname %mklibname %{name} -d -s

Summary:	Advanced IP routing and network device configuration tools
Name:		iproute2
Version:	3.4.0
Release:	1
License:	GPLv2+
Group:		Networking/Other
Url:		http://www.linuxfoundation.org/en/Net:Iproute2
Source0:	http://kernel.org/pub/linux/utils/net/iproute2/iproute2-%{version}.tar.xz
# RH patches
# rediffed from Cross LFS: http://ftp.osuosl.org/pub/clfs/clfs-packages/svn/
# (tpg) partially upstream accepted
Patch5:		iproute2-3.2.0-libdir.patch
Patch7:		iproute2-2.6.35-print-route.patch
Patch8:		iproute2-print-route-u32.patch
Patch9:		iproute2-2.6.39-create-peer-veth-without-a-name.patch
Patch10:	iproute2-2.6.39-lnstat-dump-to-stdout.patch
# MDK patches
Patch100:	iproute2-3.2.0-def-echo.patch
Patch102:	iproute2-2.4.7-bashfix.patch
Patch109:	iproute2-3.2.0-IPPROTO_IP_for_SA.patch
Patch110:	iproute2-3.2.0-q_atm-ld-uneeded.patch
BuildRequires:	bison
BuildRequires:	db5-devel
BuildRequires:	flex
BuildRequires:	kernel-source
# (oe) note: building the docs pulls in thousands of texlive packages.
%if %{build_doc}
BuildRequires:	linuxdoc-tools texlive texlive-fonts texlive-ec texlive-url
%endif
BuildRequires:	linux-atm-devel
BuildRequires:	iptables
BuildRequires:	iptables-devel
Buildrequires:	pkgconfig(libnl-1)
Requires:	iputils

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
# fedora patches
%patch5 -p1 -b .libdir
%patch7 -p1 -b .print-route
%patch8 -p1 -b .print-route-u32
%patch9 -p1 -b .peer-veth-without-name
%patch10 -p1 -b .lnstat-dump-to-stdout

# mandriva patches
%patch100 -p1 -b .def-echo
%patch102 -p1 -b .bashfix
%patch109 -p1 -b .IPPROTO_IP_for_SA
%patch110 -p1 -b .q_atm-ld-uneeded

%build
%serverbuild
%setup_compile_flags
export CFLAGS="%{optflags} -fno-strict-aliasing"
export CCOPTS="%{optflags} -ggdb -fno-strict-aliasing -D_GNU_SOURCE -Wstrict-prototypes -fPIC"
export SBINDIR=/sbin
export LIBDIR=/%{_lib}
export ARPDIR=/var/lib
export INCLUDEDIR=%{_includedir}
export IPT_LIB_DIR=/%{_lib}/iptables
export LATEST_BDB_INCLUDE_DIR=`ls -1d /usr/include/db[0-9]*`

# (tpg) don't use macro here
./configure

%make KERNEL_INCLUDE=/usr/src/linux/include LIBDIR=/%{_lib} DBM_INCLUDE=$LATEST_BDB_INCLUDE_DIR

# Doc generation fails with -j24 (ecrm1000 used before generation)
%if %{build_doc}
make -C doc
%endif

%install
rm -rf %{buildroot}

%makeinstall_std SBINDIR=/sbin LIBDIR=/%{_lib} ARPDIR=/var/lib MANDIR=%{_mandir} DOCDIR=%{_docdir}/%{name}-%{version}

mv %{buildroot}/sbin/arpd %{buildroot}/sbin/iproute-arpd

# development files
install -d %{buildroot}%{_includedir}
install -m0644 lib/libnetlink.a %{buildroot}/%{_lib}/
install -m0644 include/libnetlink.h %{buildroot}%{_includedir}/

%files
%dir %{_sysconfdir}/iproute2
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/iproute2/*
/sbin/ctstat
/sbin/genl
/sbin/ifcfg
/sbin/ifstat
/sbin/ip
/sbin/iproute-arpd
/sbin/lnstat
/sbin/nstat
/sbin/routef
/sbin/routel
/sbin/rtacct
/sbin/rtmon
/sbin/rtpr
/sbin/rtstat
/sbin/ss
/sbin/tc
/%{_lib}/tc
%{_mandir}/man7/*
%{_mandir}/man8/*
%{_mandir}/man3/*

%files -n %{staticdevelname}
%{_includedir}/*.h
/%{_lib}/*.a

%files doc
%doc README README.iproute2+tc README.decnet
%if %{build_doc}
%doc doc/*.dvi doc/*.ps 
%endif
%doc doc/Plan
%doc %{_docdir}/%{name}-%{version}/*.sgml
%doc %{_docdir}/%{name}-%{version}/*.tex
%doc %{_docdir}/%{name}-%{version}/examples
