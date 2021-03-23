The CASM Python packages
========================

The `casm-python` Python packages provide a Python interface to the CASM libraries, implement wrappers to fitting methods and DFT software, and provide other tools for plotting and analysis.

This version of `casm-python` is compatible with version 1.X of [`CASM`](https://prisms-center.github.io/CASMcode_docs/).

Development and testing:
------------------------

Install the latest tagged version of CASM 1.X. You may install CASM from source or to install the CASM conda distribution use:

    conda create -n casmpython_1.X --override-channels -c prisms-center -c defaults -c conda-forge python=3 casm-cpp=1

To install `casm-python` requirements:
    pip install -r requirements.txt

To install testing requirements, do:

    pip install -r test_requirements.txt

Use `pytest` to run the tests. To run all tests, do:

    python -m pytest -rsap tests

As an example of running a specific test, do:

    python -m pytest -rsap tests/api/test_api.py::test_API_init


Writing tests
-------------

See documentation for basics on writing tests:

- [pytest documentation](https://docs.pytest.org/en/latest/)
- Installation of the `casm` CLI and shared libraries is required for testing, but installation of the `casm-python` package itself should not be required for testing
- Keep fixtures and tests for testing each subpackage (`casm.api`, `casm.project`, etc.) independent.


Dependencies
------------

The primary dependencies are:

- **Python** Currently, we are testing using Python 3.6.  We are maintaining Python 2.7 compatibility for the near future.

- **SciPy** ([https://www.scipy.org](https://www.scipy.org)), which can be obtained using one of the methods described on their website:  [http://www.scipy.org/install.html](http://www.scipy.org/install.html). The particular SciPy packages needed are:
	- **numpy**  ([http://www.numpy.org](http://www.numpy.org))
	- **pandas** ([http://pandas.pydata.org](http://pandas.pydata.org))

- **scikit-learn** ([http://scikit-learn.org](http://scikit-learn.org))

- **deap** ([http://deap.readthedocs.io/en/master/](http://deap.readthedocs.io/en/master/)), the Distributed Evolutionary Algorithm Package, used for genetic algorithm

- **prisms_jobs** ([https://prisms-center.github.io/prisms_jobs_docs](https://prisms-center.github.io/prisms_jobs_docs))


Generating html documentation
-----------------------------
From ``CASMcode/python/casm`` directory:

	# Install sphinx requirements
	pip install -r doc_requirements.txt

	# Generate an index.rst file including all casm subpackages
	python build_doc_api_index.py

	# Generate docs
	python setup.py build_sphinx

	# Open
	open doc/build/html/index.html
