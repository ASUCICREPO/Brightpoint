import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="brightpoint",
    version="0.1.0",
    description="CDK app for Brightpoint Referral Chatbot",
    author="Administrator",
    package_dir={"": "brightpoint"},
    packages=setuptools.find_packages(where="brightpoint"),
    install_requires=[
        "aws-cdk-lib>=2.0.0",
        "constructs>=10.0.0",
        "boto3>=1.28.0",
    ],
    python_requires=">=3.9",
)