# -*- coding: utf-8 -*-

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

import pandas as pd
from scipy.io import arff

f: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/Taurus/NSL-KDD/KDDTest+1.arff"

# Load the ARFF file
data = arff.loadarff( f )

# Convert the ARFF data to a Pandas DataFrame
df = pd.DataFrame( data[ 0 ] )

# Save the DataFrame to a CSV file
df.to_csv( './output.csv', index = False )
