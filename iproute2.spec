%define build_doc 0
%define staticdevelname %mklibname %{name} -d -s
%global optflags %{optflags} -Oz
# For plugins
%define _disable_ld_no_undefined 1

Summary:	Advanced IP routing and network device configuration tools
Name:		iproute2
Version:	6.11.0
Release:	1
License:	GPLv2+
Group:		Networking/Other
Url:		http://www.linuxfoundation.org/en/Net:Iproute2
Source0:	http://kernel.org/pub/linux/utils/net/iproute2/iproute2-%{version}.tar.xz
Source1:	cbq-0000.example
Source2:	avpkt
#Patch0:		iproute2-3.19.0-docs.patch
# MDK patches

Patch100:	iproute2-3.2.0-def-echo.patch
#Patch110:	iproute2-3.2.0-q_atm-ld-uneeded.patch
Patch111:	fix-bdb-detection.patch

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	iptables
BuildRequires:	kernel-source
BuildRequires:	db-devel >= 18.1
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
export LATEST_BDB_INCLUDE_DIR=$(ls -1d /usr/include/db[0-9]* |tail -n1)

# Use /run instead of /var/run.
sed -i -e 's:/var/run:/run:g' include/namespace.h

# build against system headers
rm -r include/netinet #include/linux include/ip{,6}tables{,_common}.h include/libiptc
sed -i 's:TCPI_OPT_ECN_SEEN:16:' misc/ss.c

sed -i -e '/^CC :=/d' -e "/^HOSTCC/s:=.*:= %{__cc}:" -e "/^WFLAGS/s:-Werror::" -e "/^DBM_INCLUDE/s:=.*:=$LATEST_BDB_INCLUDE_DIR:" Makefile
sed -i "s!REPLACE_HEADERS!-I$LATEST_BDB_INCLUDE_DIR!g" configure

# (tpg) don't use macro here
./configure
echo "CFLAGS += %{optflags} -fno-strict-aliasing -Wno-error -I$LATEST_BDB_INCLUDE_DIR" >>Config
echo "HAVE_SETNS:=y" >>Config

%make_build KERNEL_INCLUDE=/usr/src/linux/include LIBDIR=%{_libdir} DBM_INCLUDE=$LATEST_BDB_INCLUDE_DIR

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
%{_bindir}/ctstat
%{_bindir}/dcb
%{_bindir}/genl
%{_bindir}/ifstat
%{_bindir}/ip
%{_bindir}/iproute-arpd
%{_bindir}/lnstat
%{_bindir}/nstat
%{_bindir}/rdma
%{_bindir}/routel
%{_bindir}/rtacct
%{_bindir}/rtmon
%{_bindir}/rtstat
%{_bindir}/ss
%{_bindir}/devlink
%{_bindir}/tipc
%{_bindir}/vdpa
%{_datadir}/iproute2
%doc %{_mandir}/man7/*
%doc %{_mandir}/man8/*
%exclude %{_mandir}/man7/tc-*
%exclude %{_mandir}/man8/tc*

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
