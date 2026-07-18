"""
Setup configuration for Web Technology Detector.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="web-tech-detector",
    version="1.0.0",
    author="Waleed Masud",
    author_email="waleed@example.com",
    description="A tool to detect technologies used by websites and generate beautiful HTML reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/waleedmasud/web-tech-detector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tech-detector=web_tech_detector.cli:main",
        ],
    },
    keywords="web technology detector scraper analyzer website tools",
    license="MIT",
)
