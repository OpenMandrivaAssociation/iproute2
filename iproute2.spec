%define build_doc 0
%define cbq_version v0.7.3
%define staticdevelname %mklibname %{name} -d -s

Summary:	Advanced IP routing and network device configuration tools
Name:		iproute2
Version:	4.20.0
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
Patch102:	iproute2-2.4.7-bashfix.patch
Patch110:	iproute2-3.2.0-q_atm-ld-uneeded.patch
Patch111:	fix-bdb-detection.patch

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	iptables
BuildRequires:	kernel-source
BuildRequires:	db6-devel
BuildRequires:	linux-atm-devel
BuildRequires:	pkgconfig(libnl-3.0)
BuildRequires:	pkgconfig(xtables)
BuildRequires:	pkgconfig(libmnl)
# (oe) note: building the docs pulls in thousands of texlive packages.
%if %{build_doc}
BuildRequires:	linuxdoc-tools
BuildRequires:	texlive
BuildRequires:	texlive-fonts
BuildRequires:	texlive-ec
BuildRequires:	texlive-url
%endif
Suggests:	iputils

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
%serverbuild
%setup_compile_flags
export
export RPM_OPT_FLAGS="%{optflags} -fno-strict-aliasing"
export CCOPTS="%{optflags} -ggdb -fno-strict-aliasing -D_GNU_SOURCE -Wstrict-prototypes -fPIC"
export SBINDIR=/sbin
export LIBDIR=/%{_lib}
export ARPDIR=/var/lib
export INCLUDEDIR=%{_includedir}
export IPT_LIB_DIR=/%{_lib}/iptables
export LATEST_BDB_INCLUDE_DIR=$(ls -1d /usr/include/db[0-9]* |tail -n1)

# Use /run instead of /var/run.
sed -i \
	-e 's:/var/run:/run:g' \
	include/namespace.h \
	man/man8/ip-netns.8

# build against system headers
rm -r include/netinet #include/linux include/ip{,6}tables{,_common}.h include/libiptc
sed -i 's:TCPI_OPT_ECN_SEEN:16:' misc/ss.c

sed -i -e '/^CC :=/d' -e "/^HOSTCC/s:=.*:= %{__cc}:" -e "/^WFLAGS/s:-Werror::" -e "/^DBM_INCLUDE/s:=.*:=$LATEST_BDB_INCLUDE_DIR:" Makefile
sed -i -e 's,#define IPT_LIB_DIR.*,#define IPT_LIB_DIR "/%{_lib}/iptables",' include/iptables.h
sed -i "s!REPLACE_HEADERS!-I$LATEST_BDB_INCLUDE_DIR!g" configure

# (tpg) don't use macro here
./configure
echo "CFLAGS += %{optflags} -fno-strict-aliasing -Wno-error -I$LATEST_BDB_INCLUDE_DIR" >>Config
echo "HAVE_SETNS:=y" >>Config

%make_build KERNEL_INCLUDE=/usr/src/linux/include LIBDIR=/%{_lib} DBM_INCLUDE=$LATEST_BDB_INCLUDE_DIR

# Doc generation fails with -j24 (ecrm1000 used before generation)
%if %{build_doc}
make -C doc
%endif

%install
export DESTDIR='%{buildroot}'
export SBINDIR='/sbin/'
export MANDIR='%{_mandir}'
export LIBDIR='/%{_lib}'
export CONFDIR='%{_sysconfdir}/iproute2'
export DOCDIR='%{_docdir}/%{name}-%{version}'
make install DESTDIR="%{buildroot}"

mv %{buildroot}/sbin/arpd %{buildroot}/sbin/iproute-arpd

# development files
install -d %{buildroot}%{_includedir}
install -m0644 lib/libnetlink.a %{buildroot}/%{_lib}/
install -m0644 include/libnetlink.h %{buildroot}%{_includedir}/

# Config files
#install -m644 etc/iproute2/* %{buildroot}%{_sysconfdir}/iproute2

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig/cbq
install -m644 %{SOURCE1} %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/cbq

install -m755 examples/cbqinit.eth1 ${DESTDIR}/${SBINDIR}/cbq

%files
%dir %{_sysconfdir}/iproute2
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/iproute2/*
/sbin/bridge
/sbin/ctstat
/sbin/genl
/sbin/ifcfg
/sbin/ifstat
/sbin/ip
/sbin/iproute-arpd
/sbin/lnstat
/sbin/nstat
/sbin/rdma
/sbin/routef
/sbin/routel
/sbin/rtacct
/sbin/rtmon
/sbin/rtpr
/sbin/rtstat
/sbin/ss
/sbin/devlink
/sbin/tipc
%{_mandir}/man7/*
%{_mandir}/man8/*
%exclude %{_mandir}/man7/tc-*
%exclude %{_mandir}/man8/tc*

%files tc
%dir %{_sysconfdir}/sysconfig/cbq
%config(noreplace) %{_sysconfdir}/sysconfig/cbq/*
%{_datadir}/bash-completion/completions/tc
%{_mandir}/man7/tc-*
%{_mandir}/man8/tc*
/%{_lib}/tc
/sbin/tc
/sbin/cbq

%files -n %{staticdevelname}
%{_includedir}/*.h
%{_includedir}/%{name}/bpf_elf.h
/%{_lib}/*.a
%{_mandir}/man3/*

%files doc
%doc README README.iproute2+tc README.decnet
%if %{build_doc}
%doc doc/*.dvi doc/*.ps
%endif
%doc %{_docdir}/%{name}-%{version}/examples
