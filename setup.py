from setuptools import setup

setup(
    name='webstat',
    version='0.2.8.4',
    description='This module enables users to inspect and export network data',
    author='Team R&D - SMILE',
    author_email='saifuddin.mohammad@smile.fr',
    url='https://git.rnd.alterway.fr/overboard/ene5ai/ene5ai-project/',
    python_requires=">=3.10",
    keywords=['webstat', 'network'],
    packages=['webstat'],
    license="BSD",
    entry_points={
        'console_scripts': ['webstat=webstat.main:main']
    },
    data_files=[
        ('share/applications/', ['webstat.desktop'])
    ],
)
