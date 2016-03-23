from setuptools import setup

# Hack to get tests to work on py2.7
try:
    import multiprocessing, logging
except Exception:
    pass

setup(
    name='tw2.dynforms',
    version='2.0.1',
    description='Dynamic form widgets for ToscaWidgets 2, a web widget toolkit.',
    long_description = open('README.rst').read().split('\n\n', 1)[1],
    author='Paul Johnston & contributors',
    author_email='toscawidgets-discuss@googlegroups.com',
    url="http://toscawidgets.org/",
    download_url="https://pypi.python.org/pypi/tw2.dynforms/",
    license="MIT",
    install_requires=[
        "tw2.core>=2.0.0",
        "tw2.forms>=2.0b4",
        "Genshi",
        ],
    packages=['tw2', 'tw2.dynforms',],
    namespace_packages = ['tw2'],
    zip_safe=False,
    include_package_data=True,
    test_suite = 'nose.collector',
    tests_require = [
        'nose',
        'formencode',
        'BeautifulSoup',
        'strainer',
        'WebTest',
        'sieve'
    ],
    entry_points="""
        [tw2.widgets]
        # Register your widgets so they can be listed in the WidgetBrowser
        widgets = tw2.dynforms
    """,
    keywords = [
        'toscawidgets.widgets',
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
