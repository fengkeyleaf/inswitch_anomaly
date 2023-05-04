import pandas as pd

df1 = pd.DataFrame({'key': ['K0', 'K1', 'K2', 'K3'],
                   'A': ['A0', 'A1', 'A2', 'A3'],
                   'B': ['B0', 'B1', 'B2', 'B3']})

df2 = pd.DataFrame({'key': ['K0', 'K1', 'K2', 'K3'],
                   'A': ['C0', 'C1', 'C2', 'C3'],
                   'B': ['D0', 'D1', 'D2', 'D3']})

result = pd.concat([df1, df2]).sort_values( by = "key", key=lambda col: col.str.lower() )

print(result)
