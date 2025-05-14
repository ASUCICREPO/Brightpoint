import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="brightpoint",
    version="0.1.0",
    description="CDK app for Brightpoint Referral Chatbot - Multi-environment",
    author="Administrator",
    package_dir={"": "brightpoint"},
    packages=setuptools.find_packages(where="brightpoint"),
    install_requires=[
        "aws-cdk-lib>=2.0.0",
        "constructs>=10.0.0",
        "boto3>=1.28.0",
        "aws-cdk.aws-amplify-alpha>=2.0.0-alpha.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)