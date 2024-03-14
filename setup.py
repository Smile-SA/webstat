from setuptools import setup, find_packages

exclude_modules = []
try:
    import prometheus_client.twisted
except ImportError:
    exclude_modules.append('prometheus_client.twisted')

setup(
    name='webstat',
    version='0.8.7',
    description='This module enables users to inspect and export network data',
    author='Team R&D - SMILE',
    author_email='saifuddin.mohammad@smile.fr',
    url='https://git.rnd.alterway.fr/overboard/ene5ai/ene5ai-project/',
    python_requires=">=3.10",
    keywords=['webstat', 'network'],
    packages=find_packages(exclude=exclude_modules),
    license="BSD",
    entry_points={
        'console_scripts': ['webstat=webstat.main:main']
    },
    data_files=[
        ('share/applications/', ['webstat.desktop'])
    ],
    package_data={'': ['webstat/*.desktop']},
)
