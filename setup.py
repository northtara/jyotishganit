from setuptools import setup, find_packages

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()



setup(
    name="jyotishganit",
    version="0.1.0",
    description="High precision Vedic astrology calculations in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NorthTara Research",
    author_email="sid@northtara.ai",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["skyfield", "pandas"],
    python_requires=">=3.8",
    license="MIT",
    url="https://github.com/northtara/jyotishganit",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Astronomy/Astrology",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="astrology vedic jyotisha astronomy calculations birth-chart",
    project_urls={
        "Bug Reports": "https://github.com/northtara/jyotishganit/issues",
        "Source": "https://github.com/northtara/jyotishganit",
    },
)
