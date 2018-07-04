from setuptools import setup

setup(name='opencog-ull',
      version='1.0.0',
      description='Unsupervised Language Learning Toolkit',
      author='Opencog ULL Team',
      url='http://github.com/singnet/language-learning',
      namespace_packages=['ull'],
      packages=['ull.grammartest', 'ull.common'],
      package_dir={'ull.common': 'src/common', 'ull.grammartest': 'src/grammar_tester'},
      scripts=['src/cli_scripts/grammar-tester', 'src/cli_scripts/parse-evaluator'],
      platform='any',
      license='MIT',
      classifiers=[
          'Development Status :: 1 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Bug Tracking',
          ],
      long_description=open('README.md').read()
      )