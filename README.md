# print_dataframe.py

Pequeno utilitário para imprimir alguns registros de um pandas.DataFrame.

Como usar

- Rodar o script de demonstração:

```powershell
python .\print_dataframe.py
```

- Importar a função em outro script:

```python
from print_dataframe import print_some_records
import pandas as pd

df = pd.DataFrame({
    'A': [1,2,3],
    'B': [4,5,6],
    'C': ['x','y','z']
})

print_some_records(df, n=2)
```

Notas
- O script assume que `pandas` está instalado (veja `requirements.txt`).
- A função checa o tipo do objeto e lida com DataFrames vazios.
