from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="famgateway",
    version="1.0.3",
    author="ARYANISPE",
    author_email="support@famgateway.in",
    description="Official Python SDK for FamGateway UPI Payment Gateway",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aryanispe/famgateway-python",
    project_urls={
        "Documentation": "https://famgateway.in/docs.php",
        "Source": "https://github.com/aryanispe/famgateway-python",
        "Tracker": "https://github.com/aryanispe/famgateway-python/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
)
