from setuptools import find_packages, setup

with open("README.rst") as fh:
    long_description = fh.read()

setup(
    name="marshmallow-annotations",
    author="Alec Nikolas Reiter",
    author_email="alecreiter@gmail.com",
    version="2.4.0",
    packages=find_packages("src", exclude=["test"]),
    package_dir={"": "src"},
    package_data={"": ["LICENSE", "README.rst", "CHANGELOG"]},
    include_package_data=True,
    description="Marrying marshmallow and annotations",
    long_description=long_description,
    install_requires=["marshmallow>=2.0.0,<3.0.0"],
    license="MIT",
    zip_safe=False,
    url="https://github.com/justanr/marshmallow-annotations",
    keywords=["annotations", "marshmallow"],
    classifiers=[
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    extras_require={"attrs": ["attrs"]},
)
