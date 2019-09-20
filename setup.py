import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="zeb_py",
  version="0.0.1",
  author="Suresh Prajapati",
  author_email="suresh.p@zebpay.com",
  description="A sample code example to execute zebpay apis for trades and other services",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="",
  packages=setuptools.find_packages(),
  classifiers=[
      "Programming Language :: Python :: 3",
      # "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
  ],
  python_requires='>=3.6',
)
