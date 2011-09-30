from setuptools import setup, find_packages

setup(
    name='tw2.dynforms',
    version='2.0a3',
    description="Dynamic widgets with JavaScript for ToscaWidgets 2",
    long_description = open('README.txt').read().split('\n\n', 1)[1],
    author='Paul Johnston & Contributors',
    author_email='paj@pajhome.org.uk',
    url = "http://toscawidgets.org/documentation/tw2.core/",
    install_requires=[
        "tw2.forms>=2.0b4",
        "Genshi",
        ],
    packages=find_packages(exclude=['ez_setup', 'tests']),
    namespace_packages = ['tw2'],
    zip_safe=False,
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
        [tw2.widgets]
        # Register your widgets so they can be listed in the WidgetBrowser
        widgets = tw2.dynforms
    """,
    keywords = [
        'toscawidgets.widgets',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
