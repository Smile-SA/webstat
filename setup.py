import os
from setuptools import setup
#from nvpy import nvpy
setup(name='webstat',
      version='1.0',
      description='This module enables users to inspect network data',
      author='Team R&D - SMILE',
      author_email='hongphuc.vu@smile.fr',
      url='https://git.rnd.alterway.fr/overboard/ene5ai/ene5ai-project/',
      install_requires=['scapy==2.4.5','numpy==1.23.1', "pandas==1.4.3", "prometheus-client==0.14.1", "pytimedinput==2.0.1"],  
      packages=['webstat'],
       license = "BSD",
      entry_points = {
        'console_scripts' : ['webstat=webstat.main:main']
                  },
      data_files = [
        ('share/applications/', ['webstat.desktop'])
                  ],     
     )
