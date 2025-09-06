from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="opportunity_assignment",
    version="1.0.0",
    description="Opportunity Assignment Management for ERPNext",
    author="Your Company",
    author_email="your-email@company.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)