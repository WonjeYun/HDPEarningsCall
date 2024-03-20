# HDPEarningsCall (WIP)
This code uses hierarchical Dirichlet process to earnings call data and do performance analysis

### Data
The data is collected from the following sources:
1. WRDS (Wharton Research Data Services)'s python API
    * Capital IQ's transcript data through SQL query
2. Yahoo Finance
    * Using yfinance python library to get stock price data

Due to WRDS being restricted access, the data is not included in the repository. If you want to use the data, please use WRDS to download the data.
The query and python code used to get the data is in the "wrds_query.py" file.

### For using the HDP Model
*Need to be done before installing required environment and libraries*
I've used "tomotopy" as the library to implement the HDP algorithm.

To install tomotopy, additional C++ libraries should be installed to your compiler if necessary.

Download "Eignen" and "EigenRand" online.
```bash
git clone https://gitlab.com/libeigen/eigen.git
git clone https://github.com/bab2min/EigenRand.git
```
Move the folder "Eigen", "EigenRand" to the following path for Mac OS.
    
```bash
/usr/local/include
```

After adding the C++ libraries to the compiler path run the following command in the terminal.

```bash
pip install tomotopy
```

### Requirements
1. The base python version is 3.10.13.
2. Create conda environment with the python version 3.10.13.
```bash
conda create -n <YourEnvName> python=3.10.13
```
3. To install the additional required libraries, run the following command in the terminal.
```bash
pip install -r requirements.txt
```
