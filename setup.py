from os.path import abspath, dirname, join
import setuptools

aboutpath = join(abspath(dirname(__file__)),'ktxo','prefect','admin', '_about.py')
_about = {}
with open(aboutpath) as fp:
    exec(fp.read(), _about)

setuptools.setup(
    name=_about["__name__"],
    version=_about["__version__"],
    author=_about["__author__"],
    author_email=_about["__author_email__"],
    description=_about["__description_message__"],
    url=_about["__url__"],
    entry_points={'console_scripts': ['prefect_wrapper = ktxo.prefect.admin.prefect_wrapper:main']},
    include_package_data=True,
    license=_about['__license__'],
    packages=setuptools.find_packages(include=['ktxo.*']),
    python_requires='>=3.8',
    install_requires=['jmespath==0.10.0','prefect==0.15.4','tabulate==0.8.9'],
    classifiers=['Programming Language :: Python :: 3.8'],
    keywords='prefect admin'
)
