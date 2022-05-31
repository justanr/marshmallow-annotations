from setuptools import find_packages, setup

with open("README.md") as fh:
    long_description = fh.read()

setup(
    name="marshmallow3-annotations",
    version="1.1.0",
    author="Alec Nikolas Reiter",
    author_email="alecreiter@gmail.com",
    packages=find_packages("src", exclude=["test"]),
    package_dir={"": "src"},
    package_data={"": ["LICENSE", "README.md", "CHANGELOG"]},
    include_package_data=True,
    description="Marrying marshmallow3 and annotations",
    long_description=long_description,
    install_requires=["marshmallow>=3.0.0"],
    license="MIT",
    zip_safe=False,
    url="https://github.com/dkunitsk/marshmallow3-annotations",
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
