# HDPEarningsCall (WIP)
This repository is the code for the MA Thesis project "Analysis of Topic Modeling on the Stock Market" by Wonje Yun, for Masters of Computational Social Sciences at University of Chicago.

The thesis and repository applies hierarchical Dirichlet process (HDP) using [tomotopy](https://github.com/bab2min/tomotopy) to earnings call data and do performance analysis.

## Data
The data is collected from the following sources:
1. Wharton Research Data Services (WRDS)'s python API
    * Capital IQ's transcript data through SQL query
    * The query for the data is not provided in the repository
    * Due to the size of the data, the querying and initial processing was done in WRDS Cloud by submitting batch jobs.
2. Yahoo Finance
    * Using yfinance python library to get stock price data

Due to WRDS being restricted access, the data is not included in the repository. If you want to use the data, please use WRDS to download the data.
The query and python code used to get the data is in the "wrds_query.py" file.

## Code Explanation
1. "utils.py"
2. "preprocessing_token.py"
3. "hdp_training.py"
4. "trend_word_change.py"
5. "evaluation.py"
6. "HDPEarningsCall.ipynb"

## Requirements
### For using the HDP Model
*Need to be done before installing required environment and libraries*

I've used [tomotopy](https://github.com/bab2min/tomotopy) as the library to implement the HDP algorithm.

To install tomotopy, additional C++ libraries should be installed to your compiler if necessary (you'll need a C++ compiler to progress).

Download [Eignen](https://gitlab.com/libeigen/eigen) and [EigenRand](https://github.com/bab2min/EigenRand) online, or git clone the repositories.
```bash
git clone https://gitlab.com/libeigen/eigen.git
git clone https://github.com/bab2min/EigenRand.git
```
Move the folder "Eigen", "EigenRand" to the compiler's "include" folder under the following path for Mac OS.
    
```bash
/usr/local/include
```
For Windows, move the folders to the compiler's "include" folder under the following path.

```bash
C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\include
```

After adding the C++ libraries to the compiler path run the following command in the terminal.

```bash
pip install tomotopy
```

### Other Requirements
1. The base python version is 3.10.13.
2. Create conda environment with the python version 3.10.13.
```bash
conda create -n <YourEnvName> python=3.10.13
```
3. To install the additional required libraries, run the following command in the terminal.
```bash
pip install -r requirements.txt
```

## For citation
```bibtex
@misc{HDPEarningsCall,
  author = {Wonje Yun},
  title = {HDP Earnings Call},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/WonjeYun/HDPEarningsCall}}
```

## Reference and License
1. Tomotopy: [MIT License](https://github.com/bab2min/tomotopy/blob/main/LICENSE)
2. Eigen: [MPL2 License](https://gitlab.com/libeigen/eigen/-/blob/master/COPYING_2_0.txt)
3. EigenRand: [MIT License](https://github.com/bab2min/tomotopy/blob/main/licenses_bundled/EigenRand)
