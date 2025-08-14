from setuptools import setup, find_packages
from pathlib import Path

README = Path(__file__).parent.joinpath("README.md").read_text(encoding="utf-8")

setup(
    name="authsimplified",
    version="0.1.0",
    author="Geoffrey Owuor",
    author_email="you@example.com",
    description="Plug-and-play Django app: JWT authentication + OTP email verification",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/geoffowuor/authsimplified",
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    install_requires=[
        "Django>=4.2",
        "djangorestframework>=3.14.0",
        "djangorestframework-simplejwt>=5.3.0",
        "pyotp>=2.9.0",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
