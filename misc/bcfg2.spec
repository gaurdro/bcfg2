%global __python python
%{!?py_ver: %global py_ver %(%{__python} -c 'import sys;print(sys.version[0:3])')}
%global pythonversion %{py_ver}
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?_initrddir: %global _initrddir %{_sysconfdir}/rc.d/init.d}

Name:             bcfg2
Version:          1.3.1
Release:          1
Summary:          Configuration management system

%if 0%{?suse_version}
# http://en.opensuse.org/openSUSE:Package_group_guidelines
Group:            System/Management
%else
Group:            Applications/System
%endif
License:          BSD
URL:              http://bcfg2.org
Source0:          ftp://ftp.mcs.anl.gov/pub/bcfg/%{name}-%{version}.tar.gz
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:        noarch

BuildRequires:    python-devel
BuildRequires:    python-lxml

%if 0%{?mandriva_version}
# mandriva seems to behave differently than other distros and needs
# this explicitly.
BuildRequires:    python-setuptools
%endif
%if 0%{?mandriva_version} == 201100
# mandriva 2011 has multiple providers for libsane, so (at least when
# building on OBS) one must be chosen explicitly: "have choice for
# libsane.so.1 needed by python-imaging: libsane1 sane-backends-iscan"
BuildRequires:    libsane1
%endif

# RHEL 5 and 6 ship with sphinx 0.6, but sphinx 1.0 is available with
# a different package name in EPEL.
%if "%{_vendor}" == "redhat" && 0%{?rhel} <= 6 && 0%{?fedora} == 0
BuildRequires:    python-sphinx10
# the python-sphinx10 package doesn't set sys.path correctly, so we
# have to do it for them
%global pythonpath %(find %{python_sitelib} -name Sphinx*.egg)
%else
BuildRequires:    python-sphinx >= 1.0
%endif

Requires:         python-lxml >= 0.9
%if 0%{?rhel_version}
# the debian init script needs redhat-lsb.
# iff we switch to the redhat one, this might not be needed anymore.
Requires:         redhat-lsb
%endif
%if "%{_vendor}" != "redhat"
# fedora and rhel (and possibly other distros) do not know this tag.
Recommends:       cron
%endif

%description
Bcfg2 helps system administrators produce a consistent, reproducible,
and verifiable description of their environment, and offers
visualization and reporting tools to aid in day-to-day administrative
tasks. It is the fifth generation of configuration management tools
developed in the Mathematics and Computer Science Division of Argonne
National Laboratory.

It is based on an operational model in which the specification can be
used to validate and optionally change the state of clients, but in a
feature unique to bcfg2 the client's response to the specification can
also be used to assess the completeness of the specification. Using
this feature, bcfg2 provides an objective measure of how good a job an
administrator has done in specifying the configuration of client
systems. Bcfg2 is therefore built to help administrators construct an
accurate, comprehensive specification.

Bcfg2 has been designed from the ground up to support gentle
reconciliation between the specification and current client states. It
is designed to gracefully cope with manual system modifications.

Finally, due to the rapid pace of updates on modern networks, client
systems are constantly changing; if required in your environment,
Bcfg2 can enable the construction of complex change management and
deployment strategies.

This package includes the Bcfg2 client software.

%package server
Version:          1.3.1
Summary:          Bcfg2 Server
%if 0%{?suse_version}
Group:            System/Management
%else
Group:            System Tools
%endif
Requires:         bcfg2 = %{version}
%if "%{py_ver}" < "2.6"
Requires:         python-ssl
%endif
Requires:         python-lxml >= 1.2.1
%if "%{_vendor}" == "redhat"
Requires:         gamin-python
%endif
%if 0%{?suse_version}
Requires:         python-python-daemon
%else
Requires:         python-daemon
%endif
Requires:         /usr/sbin/sendmail
Requires:         /usr/bin/openssl
Requires:         python-nose

%description server
Bcfg2 helps system administrators produce a consistent, reproducible,
and verifiable description of their environment, and offers
visualization and reporting tools to aid in day-to-day administrative
tasks. It is the fifth generation of configuration management tools
developed in the Mathematics and Computer Science Division of Argonne
National Laboratory.

It is based on an operational model in which the specification can be
used to validate and optionally change the state of clients, but in a
feature unique to bcfg2 the client's response to the specification can
also be used to assess the completeness of the specification. Using
this feature, bcfg2 provides an objective measure of how good a job an
administrator has done in specifying the configuration of client
systems. Bcfg2 is therefore built to help administrators construct an
accurate, comprehensive specification.

Bcfg2 has been designed from the ground up to support gentle
reconciliation between the specification and current client states. It
is designed to gracefully cope with manual system modifications.

Finally, due to the rapid pace of updates on modern networks, client
systems are constantly changing; if required in your environment,
Bcfg2 can enable the construction of complex change management and
deployment strategies.

This package includes the Bcfg2 server software.

%package server-cherrypy
Version:          1.3.1
Summary:          Bcfg2 Server - CherryPy backend
%if 0%{?suse_version}
Group:            System/Management
%else
Group:            System Tools
%endif
Requires:         bcfg2 = %{version}
Requires:         bcfg2-server = %{version}

# cherrypy 3.2.3 actually doesn't exist yet, but 3.2.2 has bugs that
# prevent it from working:
# https://bitbucket.org/cherrypy/cherrypy/issue/1154/assertionerror-in-recv-when-ssl-is-enabled
Requires:         python-cherrypy > 3.3

%description server-cherrypy
Bcfg2 helps system administrators produce a consistent, reproducible,
and verifiable description of their environment, and offers
visualization and reporting tools to aid in day-to-day administrative
tasks. It is the fifth generation of configuration management tools
developed in the Mathematics and Computer Science Division of Argonne
National Laboratory.

It is based on an operational model in which the specification can be
used to validate and optionally change the state of clients, but in a
feature unique to bcfg2 the client's response to the specification can
also be used to assess the completeness of the specification. Using
this feature, bcfg2 provides an objective measure of how good a job an
administrator has done in specifying the configuration of client
systems. Bcfg2 is therefore built to help administrators construct an
accurate, comprehensive specification.

Bcfg2 has been designed from the ground up to support gentle
reconciliation between the specification and current client states. It
is designed to gracefully cope with manual system modifications.

Finally, due to the rapid pace of updates on modern networks, client
systems are constantly changing; if required in your environment,
Bcfg2 can enable the construction of complex change management and
deployment strategies.

This package includes the Bcfg2 CherryPy server backend.

%package doc
Summary:          Configuration management system documentation
%if 0%{?suse_version}
Group:            Documentation/HTML
%else
Group:            Documentation
%endif

%description doc
Bcfg2 helps system administrators produce a consistent, reproducible,
and verifiable description of their environment, and offers
visualization and reporting tools to aid in day-to-day administrative
tasks. It is the fifth generation of configuration management tools
developed in the Mathematics and Computer Science Division of Argonne
National Laboratory.

It is based on an operational model in which the specification can be
used to validate and optionally change the state of clients, but in a
feature unique to bcfg2 the client's response to the specification can
also be used to assess the completeness of the specification. Using
this feature, bcfg2 provides an objective measure of how good a job an
administrator has done in specifying the configuration of client
systems. Bcfg2 is therefore built to help administrators construct an
accurate, comprehensive specification.

Bcfg2 has been designed from the ground up to support gentle
reconciliation between the specification and current client states. It
is designed to gracefully cope with manual system modifications.

Finally, due to the rapid pace of updates on modern networks, client
systems are constantly changing; if required in your environment,
Bcfg2 can enable the construction of complex change management and
deployment strategies.

This package includes the Bcfg2 documentation.

%package web
Version:          1.3.1
Summary:          Bcfg2 Web Reporting Interface
%if 0%{?suse_version}
Group:            System/Management
Requires:         httpd,python-django >= 1.2,python-django-south >= 0.7
%else
Group:            System Tools
Requires:         httpd,Django >= 1.2,Django-south >= 0.7
%endif
Requires:         bcfg2-server
%if "%{_vendor}" == "redhat"
Requires:         mod_wsgi
%global apache_conf %{_sysconfdir}/httpd
%else
Requires:         apache2-mod_wsgi
%global apache_conf %{_sysconfdir}/apache2
%endif

%description web
Bcfg2 helps system administrators produce a consistent, reproducible,
and verifiable description of their environment, and offers
visualization and reporting tools to aid in day-to-day administrative
tasks. It is the fifth generation of configuration management tools
developed in the Mathematics and Computer Science Division of Argonne
National Laboratory.

It is based on an operational model in which the specification can be
used to validate and optionally change the state of clients, but in a
feature unique to bcfg2 the client's response to the specification can
also be used to assess the completeness of the specification. Using
this feature, bcfg2 provides an objective measure of how good a job an
administrator has done in specifying the configuration of client
systems. Bcfg2 is therefore built to help administrators construct an
accurate, comprehensive specification.

Bcfg2 has been designed from the ground up to support gentle
reconciliation between the specification and current client states. It
is designed to gracefully cope with manual system modifications.

Finally, due to the rapid pace of updates on modern networks, client
systems are constantly changing; if required in your environment,
Bcfg2 can enable the construction of complex change management and
deployment strategies.

This package includes the Bcfg2 reports web frontend.

%prep
%setup -q -n %{name}-%{version}

%build
%{__python}%{pythonversion} setup.py build

%{?pythonpath: export PYTHONPATH="%{pythonpath}"}
%{__python}%{pythonversion} setup.py build_sphinx

%install
rm -rf %{buildroot}
%{__python}%{pythonversion} setup.py install --root=%{buildroot} --record=INSTALLED_FILES --prefix=/usr
%{__install} -d %{buildroot}%{_bindir}
%{__install} -d %{buildroot}%{_sbindir}
%{__install} -d %{buildroot}%{_initrddir}
%{__install} -d %{buildroot}%{_sysconfdir}/default
%{__install} -d %{buildroot}%{_sysconfdir}/cron.daily
%{__install} -d %{buildroot}%{_sysconfdir}/cron.hourly
%{__install} -d %{buildroot}%{_prefix}/lib/bcfg2
mkdir -p %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}
mkdir -p %{buildroot}%{_defaultdocdir}/bcfg2-server-%{version}
%if 0%{?suse_version}
%{__install} -d %{buildroot}/var/adm/fillup-templates
%endif

%{__mv} %{buildroot}%{_bindir}/bcfg2* %{buildroot}%{_sbindir}
%{__install} -m 755 debian/bcfg2.init %{buildroot}%{_initrddir}/bcfg2
%{__install} -m 755 debian/bcfg2-server.init %{buildroot}%{_initrddir}/bcfg2-server
%{__install} -m 755 debian/bcfg2-report-collector.init %{buildroot}%{_initrddir}/bcfg2-report-collector
%{__install} -m 755 debian/bcfg2.default %{buildroot}%{_sysconfdir}/default/bcfg2
%{__install} -m 755 debian/bcfg2-server.default %{buildroot}%{_sysconfdir}/default/bcfg2-server
%{__install} -m 755 debian/bcfg2.cron.daily %{buildroot}%{_sysconfdir}/cron.daily/bcfg2
%{__install} -m 755 debian/bcfg2.cron.hourly %{buildroot}%{_sysconfdir}/cron.hourly/bcfg2
%{__install} -m 755 tools/bcfg2-cron %{buildroot}%{_prefix}/lib/bcfg2/bcfg2-cron
%if 0%{?suse_version}
%{__install} -m 755 debian/bcfg2.default %{buildroot}/var/adm/fillup-templates/sysconfig.bcfg2
%{__install} -m 755 debian/bcfg2-server.default %{buildroot}/var/adm/fillup-templates/sysconfig.bcfg2-server
ln -s %{_initrddir}/bcfg2 %{buildroot}%{_sbindir}/rcbcfg2
ln -s %{_initrddir}/bcfg2-server %{buildroot}%{_sbindir}/rcbcfg2-server
%endif

cp -r tools/* %{buildroot}%{_defaultdocdir}/bcfg2-server-%{version}
cp -r build/sphinx/html/* %{buildroot}%{_defaultdocdir}/bcfg2-doc-%{version}

%{__install} -d %{buildroot}%{apache_conf}/conf.d
sed -i "s/apache2/httpd/g" misc/apache/bcfg2.conf
%{__install} -m 644 misc/apache/bcfg2.conf %{buildroot}%{apache_conf}/conf.d/wsgi_bcfg2.conf

%{__mkdir_p} %{buildroot}%{_localstatedir}/cache/%{name}
%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/%{name}

# mandriva and RHEL 5 cannot handle %ghost without the file existing,
# so let's touch a bunch of empty config files
touch %{buildroot}%{_sysconfdir}/bcfg2.conf \
    %{buildroot}%{_sysconfdir}/bcfg2-web.conf

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot} || exit 2

%files
%defattr(-,root,root,-)
%{_sbindir}/bcfg2
%dir %{python_sitelib}/Bcfg2
%{python_sitelib}/Bcfg2/Compat.py*
%{python_sitelib}/Bcfg2/__init__.py*
%{python_sitelib}/Bcfg2/Logger.py*
%{python_sitelib}/Bcfg2/Options.py*
%{python_sitelib}/Bcfg2/Proxy.py*
%{python_sitelib}/Bcfg2/Utils.py*
%{python_sitelib}/Bcfg2/version.py*
%{python_sitelib}/Bcfg2/Client
%{_mandir}/man1/bcfg2.1*
%{_mandir}/man5/bcfg2.conf.5*
%{_initrddir}/bcfg2
%config(noreplace) %{_sysconfdir}/default/bcfg2
%{_sysconfdir}/cron.hourly/bcfg2
%{_sysconfdir}/cron.daily/bcfg2
%{_prefix}/lib/bcfg2/bcfg2-cron
%{_localstatedir}/cache/%{name}
%{_localstatedir}/lib/%{name}
%if 0%{?suse_version}
%{_sbindir}/rcbcfg2
%config(noreplace) /var/adm/fillup-templates/sysconfig.bcfg2
%endif
%ghost %config(noreplace,missingok) %attr(0600,root,root) %{_sysconfdir}/bcfg2.conf

%files server
%defattr(-,root,root,-)
%{_initrddir}/bcfg2-server
%{_initrddir}/bcfg2-report-collector
%dir %{python_sitelib}/Bcfg2
%{python_sitelib}/Bcfg2/Cache.py*
%{python_sitelib}/Bcfg2/Encryption.py*
%{python_sitelib}/Bcfg2/SSLServer.py*
%{python_sitelib}/Bcfg2/Statistics.py*
%{python_sitelib}/Bcfg2/manage.py*
%{python_sitelib}/Bcfg2/settings.py*
%{python_sitelib}/Bcfg2/Server
%{python_sitelib}/Bcfg2/Reporting
%exclude %{python_sitelib}/Bcfg2/Server/CherryPyCore.py

%{python_sitelib}/*egg-info

%dir %{_datadir}/bcfg2
%{_datadir}/bcfg2/Hostbase
%{_datadir}/bcfg2/schemas
%{_datadir}/bcfg2/xsl-transforms
%config(noreplace) %{_sysconfdir}/default/bcfg2-server
%{_sbindir}/bcfg2-admin
%{_sbindir}/bcfg2-build-reports
%{_sbindir}/bcfg2-crypt
%{_sbindir}/bcfg2-info
%{_sbindir}/bcfg2-lint
%{_sbindir}/bcfg2-repo-validate
%{_sbindir}/bcfg2-reports
%{_sbindir}/bcfg2-report-collector
%{_sbindir}/bcfg2-server
%{_sbindir}/bcfg2-yum-helper
%{_sbindir}/bcfg2-test
%if 0%{?suse_version}
%{_sbindir}/rcbcfg2-server
%config(noreplace) /var/adm/fillup-templates/sysconfig.bcfg2-server
%endif

%{_mandir}/man5/bcfg2-lint.conf.5*
%{_mandir}/man8/*.8*
%dir %{_prefix}/lib/bcfg2
%ghost %config(noreplace,missingok) %attr(0600,root,root) %{_sysconfdir}/bcfg2.conf

%doc %{_defaultdocdir}/bcfg2-server-%{version}

%files server-cherrypy
%defattr(-,root,root,-)
%{python_sitelib}/Bcfg2/Server/CherryPyCore.py

%files doc
%defattr(-,root,root,-)
%doc %{_defaultdocdir}/bcfg2-doc-%{version}

%files web
%defattr(-,root,root,-)
%{_datadir}/bcfg2/reports.wsgi
%{_datadir}/bcfg2/site_media
%dir %{apache_conf}
%dir %{apache_conf}/conf.d
%config(noreplace) %{apache_conf}/conf.d/wsgi_bcfg2.conf
%ghost %config(noreplace,missingok) %attr(0640,root,apache) %{_sysconfdir}/bcfg2-web.conf

%post server
# enable daemon on first install only (not on update).
if [ $1 -eq 1 ]; then
%if 0%{?suse_version}
  %fillup_and_insserv -f bcfg2-server
%else
  /sbin/chkconfig --add bcfg2-server
%endif
fi

%preun
%if 0%{?suse_version}
# stop on removal (not on update).
if [ $1 -eq 0 ]; then
  %stop_on_removal bcfg2
fi
%endif

%preun server
%if 0%{?suse_version}
if [ $1 -eq 0 ]; then
  %stop_on_removal bcfg2-server
  %stop_on_removal bcfg2-report-collector
fi
%endif

%postun
%if 0%{?suse_version}
if [ $1 -eq 0 ]; then
  %insserv_cleanup
fi
%endif

%postun server
%if 0%{?suse_version}
if [ $1 -eq 0 ]; then
  # clean up on removal.
  %insserv_cleanup
fi
%endif

%changelog
* Thu Mar 21 2013 Sol Jerome <sol.jerome@gmail.com> 1.3.1-1
- New upstream release

* Fri Mar 15 2013 Sol Jerome <sol.jerome@gmail.com> 1.3.0-0.0
- New upstream release

* Tue Jan 29 2013 Sol Jerome <sol.jerome@gmail.com> 1.3.0-0.0rc2
- New upstream release

* Wed Jan 09 2013 Sol Jerome <sol.jerome@gmail.com> 1.3.0-0.0rc1
- New upstream release

* Tue Oct 30 2012 Sol Jerome <sol.jerome@gmail.com> 1.3.0-0.0pre2
- New upstream release

* Wed Oct 17 2012 Chris St. Pierre <chris.a.st.pierre@gmail.com> 1.3.0-0.2pre1
- Split bcfg2-selinux into its own specfile

* Fri Sep 14 2012 Chris St. Pierre <chris.a.st.pierre@gmail.com> 1.3.0-0.1pre1
- Added -selinux subpackage

* Fri Aug 31 2012 Sol Jerome <sol.jerome@gmail.com> 1.3.0-0.0pre1
- New upstream release

* Wed Aug 15 2012 Chris St. Pierre <chris.a.st.pierre@gmail.com> 1.2.3-0.1
- Added tools/ as doc for bcfg2-server subpackage

* Sat Feb 18 2012 Christopher 'm4z' Holm <686f6c6d@googlemail.com> 1.2.1
- Added Fedora and Mandriva compatibilty (for Open Build Service).
- Added missing dependency redhat-lsb.

* Tue Feb 14 2012 Christopher 'm4z' Holm <686f6c6d@googlemail.com> 1.2.1
- Added openSUSE compatibility.
- Various changes to satisfy rpmlint.

* Thu Jan 27 2011 Chris St. Pierre <chris.a.st.pierre@gmail.com> 1.2.0pre1-0.0
- Added -doc sub-package

* Mon Jun 21 2010 Fabian Affolter <fabian@bernewireless.net> - 1.1.0rc3-0.1
- Changed source0 in order that it works with spectool

* Fri Feb 2 2007 Mike Brady <mike.brady@devnull.net.nz> 0.9.1
- Removed use of _libdir due to Red Hat x86_64 issue.

* Fri Dec 22 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-5
- Server needs client library files too so put them in main package

* Wed Dec 20 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-4
- Yes, actually we need to require openssl

* Wed Dec 20 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-3
- Don't generate SSL cert in post script, it only needs to be done on
  the server and is handled by the bcfg2-admin tool.
- Move the /etc/bcfg2.key file to the server package
- Don't install a sample copy of the config file, just ghost it
- Require gamin-python for the server package
- Don't require openssl
- Make the client a separate package so you don't have to have the
  client if you don't want it

* Wed Dec 20 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-2
- Add more documentation

* Mon Dec 18 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.8.7.1-1
- First version for Fedora Extras

* Fri Sep 15 2006 Narayan Desai <desai@mcs.anl.gov> - 0.8.4-1
- Initial log
