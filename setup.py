from setuptools import setup
_requirements = [
  "pandas",
  "prometheus-client==0.15.0",
  "psutil"  
  ]

setup(name='webstat',
      version='0.1',
      description='This module enables users to inspect and export network data',
      author='Team R&D - SMILE',
      author_email='saifuddin.mohammad@smile.fr',
      url='https://git.rnd.alterway.fr/overboard/ene5ai/ene5ai-project/',
      python_requires= ">=3.6 , <4.0",
      install_requires=_requirements,
      keywords = ['webstat', 'network'],
      packages=['webstat'],
       license = "BSD",
      entry_points = {
        'console_scripts' : ['webstat=webstat.main:main']
                  },
      data_files = [
        ('share/applications/', ['webstat.desktop'])
                  ],     
     )
