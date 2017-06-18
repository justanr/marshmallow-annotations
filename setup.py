from setuptools import setup

with open('README.rst') as fh:
    long_description = fh.read()

setup(
    name='marshmallow-annotations',
    author='Alec Nikolas Reiter',
    author_email='alecreiter@gmail.com',
    version='1.0.0',
    py_modules=['marshmallow_annotations'],
    description='Allows declaring marshmallow fields as annotations',
    long_description=long_description,
    install_requires=['marshmallow'],
    license='MIT',
    zip_safe=False,
    url='https://github.com/justanr/marshmallow-annotations',
    keywords=['annotations', 'marshmallow'],
    classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython'
    ]
)
