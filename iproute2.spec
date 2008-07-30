%define snap 0
%if %{snap}
%define fver %version-%snap
%else
%define fver %version
%endif

%define staticdevelname %mklibname %{name} -d -s

Summary: 	Advanced IP routing and network device configuration tools
Name:		iproute2
Version:	2.6.26
Release:	%mkrel 1
License:	GPL
Group:		Networking/Other
Url:		http://linux-net.osdl.org/index.php/Iproute2
Source0:	%{name}-%fver.tar.bz2
Source2:	iproute2-man8.tar.bz2
# RH patches
#Patch5 is fscking compilation against kernel22 in rh
Patch6:		iproute2-flags.patch
# rediffed from Cross LFS: http://ftp.osuosl.org/pub/clfs/clfs-packages/svn/
Patch8:		iproute2-2.6.26-libdir.patch
# MDK patches
Patch100:	iproute2-def-echo.patch
Patch101:	iproute2-2.6.26-ccopts.patch
Patch102:	iproute2-2.4.7-bashfix.patch
Patch105:	iproute2-mult-deflt-gateways.patch
Patch106:	iproute2-2.6.X-ss040702-build-fix.patch
BuildRequires:	bison
BuildRequires:	db4-devel
BuildRequires:	flex
BuildRequires:	kernel-source
BuildRequires:	linuxdoc-tools
BuildRequires:  linux-atm-devel
Requires:	iputils
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The iproute package contains networking utilities (ip, tc and rtmon, for
example) which are designed to use the advanced networking capabilities of the
Linux 2.2.x kernels and later,  such as policy routing, fast NAT and packet
scheduling.

%package -n	%{staticdevelname}
Summary:	Development files for iproute2
Group:  	Development/C
Provides:	iproute2-devel = %{version}-%{release}

%description -n	%{staticdevelname}
The iproute package contains networking utilities (ip, tc and rtmon, for
example) which are designed to use the advanced networking capabilities of the
Linux 2.2.x kernels and later,  such as policy routing, fast NAT and packet
scheduling.

This package contains development files for iproute2.

%package	doc
Summary:	Documentation for Advanced IP routing and network device configuration tools
Group:  	Networking/Other

%description	doc
Documentation for iproute

%prep

%setup -q -n %{name}-%fver
%patch6 -p1 -b .flags
%patch8 -p1 -b .libdir

%patch100 -p1
%patch101 -p1 -b .ccopts
%patch102 -p1 -b .bashfix
#%patch105 -p1 -b .make
%patch106 -p1 -b .build

%build
%serverbuild
export CCOPTS="%{optflags} -ggdb"
export SBINDIR=/sbin
export LIBDIR=%{_libdir}
export VARLIB=/var/lib
export INCLUDEDIR=%{_includedir}

# (tpg) set explicit path for iptables
sed -i -e 's#IPT_PATH#/%{_lib}/iptables#g' include/iptables.h

%make KERNEL_INCLUDE=/usr/src/linux/include LIBDIR=%{_libdir}
%make -C doc

%install
rm -rf %{buildroot}

%makeinstall_std SBINDIR=/sbin LIBDIR=%{_libdir} VARLIB=/var/lib
mv %{buildroot}/share %{buildroot}%{_prefix}

mv %{buildroot}/sbin/arpd %{buildroot}/sbin/iproute-arpd

# do not add q_atm.so for the moment, as it will pull libatm, and 
# iproute is required by basesystem
rm %{buildroot}%{_libdir}/tc/q_atm.so
mv %{buildroot}%{_docdir}/%{name} %{buildroot}%{_docdir}/%{name}-%{version}
tar -jxf %{SOURCE2} -C %{buildroot}%{_mandir}

# development files
install -d %{buildroot}%{_libdir}
install -d %{buildroot}%{_includedir}
install -m0644 lib/libnetlink.a %{buildroot}%{_libdir}/
install -m0644 include/libnetlink.h %{buildroot}%{_includedir}/

%clean
rm -rf %{buildroot}

%files
%defattr (-,root,root)
%dir %{_sysconfdir}/iproute2
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/iproute2/*
/sbin/*
%_mandir/man8/*
%_mandir/man3/*
%_libdir/tc/

%files -n %{staticdevelname}
%defattr (-,root,root)
%{_includedir}/*.h
%{_libdir}/*.a

%files doc
%defattr (-,root,root)
%doc README README.iproute2+tc RELNOTES README.decnet
%doc doc/*.dvi doc/*.ps doc/Plan
%doc %{_docdir}/%{name}-%{version}/*.sgml
%doc %{_docdir}/%{name}-%{version}/*.tex
%doc %{_docdir}/%{name}-%{version}/examples
