%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%global modname tw2.dynforms

Name:           python-tw2-dynforms
Version:        2.0.0
Release:        2%{?dist}
Summary:        Dynamic forms for ToscaWidgets2

Group:          Development/Languages
License:        MIT
URL:            http://toscawidgets.org
Source0:        http://pypi.python.org/packages/source/t/%{modname}/%{modname}-%{version}.tar.gz
BuildArch:      noarch

# For building
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-tw2-core
BuildRequires:  python-tw2-forms
BuildRequires:  python-genshi

# For tests
BuildRequires:  python-nose
BuildRequires:  python-formencode
BuildRequires:  python-BeautifulSoup
BuildRequires:  python-strainer
BuildRequires:  python-webtest

# Runtime requirements
Requires:       python-tw2-core
Requires:       python-tw2-forms
Requires:       python-genshi

%description
ToscaWidgets is a web widget toolkit for Python to aid in the creation,
packaging and distribution of common view elements normally used in the web.

tw2.dynforms includes dynamic form building widgets that use JavaScript.

%prep
%setup -q -n %{modname}-%{version}

%if %{?rhel}%{!?rhel:0} >= 6

# Make sure that epel/rhel picks up the correct version of webob
awk 'NR==1{print "import __main__; __main__.__requires__ = __requires__ = [\"WebOb>=1.0\"]; import pkg_resources"}1' setup.py > setup.py.tmp
mv setup.py.tmp setup.py

# Remove all the fancy nosetests configuration for older python
rm setup.cfg

%endif


%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}

%check
PYTHONPATH=$(pwd) python setup.py test

%files
%doc README.rst
%{python_sitelib}/*

%changelog
* Wed May 02 2012 Ralph Bean <rbean@redhat.com> - 2.0.0-2
- Removed clean section
- Removed defattr in files section
- Removed unnecessary references to buildroot

* Wed Apr 11 2012 Ralph Bean <rbean@redhat.com> - 2.0.0-1
- Initial packaging for Fedora
