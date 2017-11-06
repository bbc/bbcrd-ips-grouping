%global module_name ipsgrouping

Name:           python-grouping
Version:        0.1.0
Release:        1%{?dist}
License:        Internal Licence
Summary:        Grouping API

Source0:        %{name}-%{version}.tar.gz
Source1:        ips-grouping.service

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-nmoscommon
BuildRequires:  python-nose
BuildRequires:  python-mock

Requires:       python
Requires:       ips-reverseproxy-common
Requires:       python-nmoscommon
Requires:       python-jsonschema
Requires:       mongodb
Requires:       mongodb-server
Requires:       python-pymongo

%{?systemd_requires}

%description
Grouping API

%prep
%setup -n %{name}-%{version}

%build
%{py2_build}

%install
%{py2_install}

# Install systemd unit file
install -D -p -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/ips-grouping.service

# Install Apache config file
install -D -p -m 0644 etc/apache2/sites-available/ips-api-grouping-v1_0.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/ips-apis/ips-api-grouping-v1_0.conf

%pre
getent group ipstudio >/dev/null || groupadd -r ipstudio
getent passwd ipstudio >/dev/null || \
    useradd -r -g ipstudio -d /dev/null -s /sbin/nologin \
        -c "IP Studio user" ipstudio

%post
chown -R ipstudio:ipstudio /etc/ips-grouping
%systemd_post ips-grouping.service
systemctl enable mongod
systemctl start mongod
systemctl start ips-grouping
systemctl reload httpd

%preun
systemctl stop ips-grouping

%clean
rm -rf %{buildroot}

%files
%{_bindir}/ips-grouping
%{_bindir}/ips-grouping-import-dump

%{_unitdir}/ips-grouping.service

%{python2_sitelib}/%{module_name}
%{python2_sitelib}/python_grouping-%{version}*.egg-info

%defattr(-,ipstudio, ipstudio,-)
%config %{_sysconfdir}/httpd/conf.d/ips-apis/ips-api-grouping-v1_0.conf

%config %{_sysconfdir}/ips-grouping/config.json

%changelog
* Thu Aug 03 2017 Sam Nicholson <sam.nicholson@bbc.co.uk> - 0.1.0-1
- Initial packaging for RPM
