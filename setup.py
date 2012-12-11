from setuptools import setup

setup(
    name="dynadotpy",
    version="0.1.0",
    description='Simple Python wrapper for dynadot.com v2 API.',
    long_description='Simple Python wrapper for dynadot.com v2 API.',
    keywords="python, dynadot",
    author="Chris Jones <chris@brack3t.com>",
    author_email="chris@brack3t.com",
    url="https://github.com/brack3t/dynadotpy",
    license="BSD",
    packages=["dynadotpy"],
    zip_safe=False,
    install_requires=["requests"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2 :: Only",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Intended Audience :: Information Technology"
    ],
)
