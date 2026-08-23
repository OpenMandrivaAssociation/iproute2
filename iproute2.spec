%define build_doc 0
%define staticdevelname %mklibname %{name} -d -s
%global optflags %{optflags} -Oz
# For plugins
%define _disable_ld_no_undefined 1

Summary:	Advanced IP routing and network device configuration tools
Name:		iproute2
Version:	7.1.0
Release:	1
License:	GPLv2+
Group:		Networking/Other
Url:		https://www.linuxfoundation.org/en/Net:Iproute2
Source0:	https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/snapshot/iproute2-%{version}.tar.gz
Source1:	cbq-0000.example
Source2:	avpkt
#Patch0:		iproute2-3.19.0-docs.patch
# MDK patches

Patch100:	iproute2-3.2.0-def-echo.patch
#Patch110:	iproute2-3.2.0-q_atm-ld-uneeded.patch
Patch111:	iproute2-7.1.0-arpd-lmdb.patch

BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool-base
BuildRequires:	slibtool
BuildRequires:	make
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	iptables
BuildRequires:	kernel-source
BuildRequires:	pkgconfig(lmdb)
BuildRequires:	linux-atm-devel
BuildRequires:	pkgconfig(libnl-3.0)
BuildRequires:	pkgconfig(xtables)
BuildRequires:	pkgconfig(libmnl)
BuildRequires:	pkgconfig(libbpf)
# (oe) note: building the docs pulls in thousands of texlive packages.
%if %{build_doc}
BuildRequires:	linuxdoc-tools
BuildRequires:	texlive
BuildRequires:	texlive-fonts
BuildRequires:	texlive-ec
BuildRequires:	texlive-url
%endif
Suggests:	iputils
# For compatibility with some other distros - a few 3rd party
# binaries (e.g. tailscale) put this as dependency
%rename iproute

%description
The iproute package contains networking utilities (ip, tc and rtmon, for
example) which are designed to use the advanced networking capabilities of the
Linux 2.2.x kernels and later,  such as policy routing, fast NAT and packet
scheduling.

%package -n %{staticdevelname}
Summary:	Development files for iproute2
Group:		Development/C
Provides:	iproute2-devel = %{EVRD}

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

%package tc
Summary:	Linux Traffic Control utility
Group:		Networking/Other
License:	GPLv2+
Obsoletes:	%{name} < 4.5.0
Requires:	%{name} = %{EVRD}

%description tc
The Traffic Control utility manages queueing disciplines, their classes and
attached filters and actions. It is the standard tool to configure QoS in
Linux.

%package arpd
Summary:	Userspace ARP helper daemon
Group:		Networking/Other
Requires:	%{name} = %{EVRD}

%description arpd
arpd collects gratuitous ARP information and can feed it to the kernel
to avoid redundant broadcasts when the kernel ARP cache is too small.
The daemon is stored as iproute-arpd so it does not collide with other
arpd implementations.

%package rtmon
Summary:	Listen to and dump kernel routing changes
Group:		Networking/Other
Requires:	%{name} = %{EVRD}

%description rtmon
rtmon listens to netlink route updates and writes them to a file.

%package rtacct
Summary:	Network statistics collector (nstat companion)
Group:		Networking/Other
Requires:	%{name} = %{EVRD}

%description rtacct
rtacct displays and collects network statistics from /proc/net/rt_acct
and related kernel counters.

%package routel
Summary:	Format ip route output as a table
Group:		Networking/Other
Requires:	%{name} = %{EVRD}

%description routel
routel is a small helper that pretty-prints the routing table.

%package lnstat
Summary:	Legacy lnstat/rtstat/ctstat network statistics tools
Group:		Networking/Other
Requires:	%{name} = %{EVRD}

%description lnstat
lnstat and the rtstat/ctstat compatibility names are the old iproute2
statistics tools. They are not needed to use ip, ss, tc or bridge.

%prep
%autosetup -p1
sed -i "s/_VERSION_/%{version}/" man/man8/ss.8

%build
%set_build_flags

export RPM_OPT_FLAGS="%{optflags} -fno-strict-aliasing"
export CCOPTS="%{optflags} -ggdb -fno-strict-aliasing -D_GNU_SOURCE -Wstrict-prototypes -fPIC"
export SBINDIR=%{_sbindir}
export LIBDIR=%{_libdir}
export ARPDIR=/var/lib
export INCLUDEDIR=%{_includedir}
export IPT_LIB_DIR=%{_libdir}/iptables
# Use /run instead of /var/run.
sed -i -e 's:/var/run:/run:g' include/namespace.h

# build against system headers
rm -r include/netinet #include/linux include/ip{,6}tables{,_common}.h include/libiptc
sed -i 's:TCPI_OPT_ECN_SEEN:16:' misc/ss.c

sed -i -e '/^CC :=/d' -e "/^HOSTCC/s:=.*:= %{__cc}:" -e "/^WFLAGS/s:-Werror::" Makefile

# (tpg) don't use macro here
./configure
echo "CFLAGS += %{optflags} -fno-strict-aliasing -Wno-error" >>Config
echo "HAVE_SETNS:=y" >>Config

%if %{cross_compiling}
%global iproute_kernel_include /usr/%{_target_platform}/usr/include
%else
%global iproute_kernel_include /usr/src/linux/include
%endif
%make_build KERNEL_INCLUDE=%{iproute_kernel_include} LIBDIR=%{_libdir}

# Doc generation fails with -j24 (ecrm1000 used before generation)
%if %{build_doc}
make -C doc
%endif

%install
export DESTDIR='%{buildroot}'
export SBINDIR='%{_bindir}'
export MANDIR='%{_mandir}'
export LIBDIR='%{_libdir}'
export CONFDIR='%{_sysconfdir}/iproute2'
export DOCDIR='%{_docdir}/%{name}-%{version}'
make install DESTDIR="%{buildroot}" LIBDIR="%{_libdir}"

mv %{buildroot}%{_bindir}/arpd %{buildroot}%{_bindir}/iproute-arpd

# LMDB MDB_NOSUBDIR uses the -b path as the data file and path-lock as the lock.
install -d %{buildroot}%{_localstatedir}/lib/arpd
touch %{buildroot}%{_localstatedir}/lib/arpd/arpd.db
touch %{buildroot}%{_localstatedir}/lib/arpd/arpd.db-lock

# development files
install -d %{buildroot}%{_includedir}
install -m0644 lib/libnetlink.a %{buildroot}%{_libdir}/
install -m0644 include/libnetlink.h %{buildroot}%{_includedir}/

# Config files
mkdir -p %{buildroot}%{_sysconfdir}/iproute2

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig/cbq
install -m644 %{SOURCE1} %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/cbq

%files
%dir %{_sysconfdir}/iproute2
%{_bindir}/bridge
%{_bindir}/dcb
%{_bindir}/dpll
%{_bindir}/genl
%{_bindir}/ifstat
%{_bindir}/ip
%{_bindir}/netshaper
%{_bindir}/nstat
%{_bindir}/rdma
%{_bindir}/ss
%{_bindir}/devlink
%{_bindir}/tipc
%{_bindir}/vdpa
%{_datadir}/iproute2
%{_datadir}/bash-completion/completions/dpll
%doc %{_mandir}/man7/*
%doc %{_mandir}/man8/*
%exclude %{_mandir}/man7/tc-*
%exclude %{_mandir}/man8/tc*
%exclude %{_mandir}/man8/arpd*
%exclude %{_mandir}/man8/rtmon*
%exclude %{_mandir}/man8/rtacct*
%exclude %{_mandir}/man8/routel*
%exclude %{_mandir}/man8/lnstat*
%exclude %{_mandir}/man8/rtstat*
%exclude %{_mandir}/man8/ctstat*

%files arpd
%{_bindir}/iproute-arpd
%dir %{_localstatedir}/lib/arpd
%ghost %{_localstatedir}/lib/arpd/arpd.db
%ghost %{_localstatedir}/lib/arpd/arpd.db-lock
%doc %{_mandir}/man8/arpd.8*

%files rtmon
%{_bindir}/rtmon
%doc %{_mandir}/man8/rtmon.8*

%files rtacct
%{_bindir}/rtacct
%doc %{_mandir}/man8/rtacct.8*

%files routel
%{_bindir}/routel
%doc %{_mandir}/man8/routel.8*

%files lnstat
%{_bindir}/lnstat
%{_bindir}/rtstat
%{_bindir}/ctstat
%doc %{_mandir}/man8/lnstat.8*
%doc %{_mandir}/man8/rtstat.8*
%doc %{_mandir}/man8/ctstat.8*

%files tc
%dir %{_sysconfdir}/sysconfig/cbq
%config(noreplace) %{_sysconfdir}/sysconfig/cbq/*
%{_datadir}/bash-completion/completions/tc
%{_datadir}/bash-completion/completions/devlink
%doc %{_mandir}/man7/tc-*
%doc %{_mandir}/man8/tc*
%{_libdir}/tc
%{_bindir}/tc

%files -n %{staticdevelname}
%{_includedir}/*.h
%{_includedir}/%{name}/bpf_elf.h
%{_libdir}/*.a
%doc %{_mandir}/man3/*

%files doc
%doc README
%if %{build_doc}
%doc doc/*.dvi doc/*.ps
%endif
