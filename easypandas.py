import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
import re
import matplotlib.pyplot as plt
import seaborn as sns

from easyplot import familystat # Importas la función específica
class easypandas:
    """
    ptranslate: Educational wrapper around pandas DataFrame.

    This class provides a simplified interface for students who are learning
    data analysis. It hides some of the complexity of pandas while still
    allowing access to its power.

    Example:
        P = ptranslate(data)

        P.qty
        P.show()
        P.mean("age")
        P.where("age > 30")
    """

    def __init__(self, data, **kwargs):
        """
        Create a new easypandas object.
    
        Parameters
        ----------
        data : str, dict, list, np.ndarray, or DataFrame
            - str: path to CSV file or Excel file
            - dict: dictionary to convert to DataFrame
            - list: list to convert to DataFrame
            - np.ndarray: array to convert to DataFrame
            - DataFrame: existing pandas DataFrame
        
        **kwargs : additional arguments passed to pandas read methods
            For Excel: sheet_name, header, usecols, etc.
            For CSV: sep, encoding, header, etc.
            For JSON: orient, lines, etc.
        
        Examples
        --------
        P = easypandas("data.csv")
        P = easypandas("data.xlsx", sheet_name="results")
        P = easypandas({"name": ["Ana", "Juan"], "age": [25, 32]})
        P = easypandas([[1,2,3], [4,5,6]])
        P = easypandas(df)  # existing DataFrame
        """
        
        # Dictionary mapping file extensions to pandas read functions
        readers = {
            '.csv': pd.read_csv,
            '.xlsx': pd.read_excel,
            '.xls': pd.read_excel,
            '.xlsm': pd.read_excel,
            '.json': pd.read_json,
            '.parquet': pd.read_parquet,
            '.feather': pd.read_feather,
            '.pkl': pd.read_pickle,
            '.pickle': pd.read_pickle,
            '.html': lambda f, **kw: pd.read_html(f, **kw)[0],  # take first table
            '.txt': pd.read_csv,  # will use kwargs (sep='\t' by default if not specified)
        }
 
        if '.sqlite' in data:
            import sqlite3
            conn = sqlite3.connect(data)
            df = pd.read_sql("SELECT * FROM Customer", conn)
            self.df=df
            return 
        # Case 1: Already a DataFrame
        if isinstance(data, pd.DataFrame):
            self.df = data.copy()
            return
        
        # Case 2: String - file path
        if isinstance(data, str):
            import os
            
            # Check if file exists
            if not os.path.exists(data) and '.' in data:
                # Try common data directories
                for prefix in ['', './', './data/', '../data/', '/data/']:
                    test_path = f"{prefix}{data}" if prefix else data
                    if os.path.exists(test_path):
                        data = test_path
                        break
                else:
                    raise FileNotFoundError(f"File '{data}' not found")
            
            # Get file extension
            ext = os.path.splitext(data)[1].lower()
            
            # Find appropriate reader
            if ext in readers:
                reader = readers[ext]
                
                # Special handling for Excel files with better engine selection
                if ext in ['.xlsx', '.xls', '.xlsm']:
                    try:
                        # Try fastest engine first for modern Excel files
                        if ext in ['.xlsx', '.xlsm']:
                            try:
                                self.df = pd.read_excel(data, engine='calamine', **kwargs)
                            except ImportError:
                                # Fallback to openpyxl if calamine not installed
                                self.df = pd.read_excel(data, engine='openpyxl', **kwargs)
                        else:  # .xls old format
                            self.df = pd.read_excel(data, engine='xlrd', **kwargs)
                    except ImportError as e:
                        # Clear error message
                        if 'calamine' in str(e):
                            pkg = 'python-calamine'
                            cmd = 'pip install python-calamine'
                        elif 'openpyxl' in str(e):
                            pkg = 'openpyxl'
                            cmd = 'pip install openpyxl'
                        else:
                            pkg = 'xlrd'
                            cmd = 'pip install xlrd'
                        
                        raise ImportError(
                            f"❌ Cannot read '{data}'. Missing package '{pkg}'.\n"
                            f"💻 Install with: {cmd}\n"
                            f"🔍 Original error: {e}"
                        )
                else:
                    # Special handling for TXT files (default to tab separator if not specified)
                    if ext == '.txt' and 'sep' not in kwargs and 'delimiter' not in kwargs:
                        kwargs['sep'] = '\t'
                    
                    self.df = reader(data, **kwargs)
            else:
                raise ValueError(f"Unsupported file extension '{ext}'. Supported: {list(readers.keys())}")
            return
        
        # Case 3: All other cases (dict, list, array, etc.)
        try:
            self.df = pd.DataFrame(data, **kwargs)
        except Exception as e:
            raise TypeError(
                f"Cannot create DataFrame from {type(data)}. "
                f"Supported: DataFrame, file path (str), dict, list, tuple, np.ndarray. Error: {e}"
            )  

    # ---------------------------------
    # Redirect unknown attributes to pandas
    # ---------------------------------
    def __getattr__(self, name):
        attr = getattr(self.df, name)
    
        if callable(attr):
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                
                if isinstance(result, pd.DataFrame):
                    return easypandas(result)
                
                return result
            
            return wrapper
        
        return attr
 
    # ---------------------------------
    # Call method for selection
    # ---------------------------------
 
    def __repr__(self):
        """Muestra el DataFrame directamente"""
        return repr(self.df)
    
    def __str__(self):
        """Muestra el DataFrame con print()"""
        return str(self.df)
    
    def __dir__(self):
        """
        Improve autocomplete: include easypandas + pandas methods
        """
        return list(set(
            dir(self.__class__) +      # métodos de easypandas
            list(self.__dict__.keys()) +
            dir(self.df)            # métodos de pandas
        )) 
    def __call__(self, *args):
        """
        Allows MATLAB/NumPy style selection.
        
        Examples:
        --------
        P(3)               # Row 3 (as DataFrame)
        P(3, ":")          # Row 3, all columns
        P(0, 3)            # Rows 0 to 3 (inclusive)
        P(0, 3, "A")       # Rows 0-3, column A
        P(0, 3, "A", "B")  # Rows 0-3, columns A and B
        P("A")             # Row with index 'A' (if exists)
        P("A:D")           # Columns from A to D
        P("Monday", "Wednesday")  # Range by index labels (NEW!)
        P()                # Full DataFrame
        """
     
        df = self.df
        
        if len(args) == 0:
            return df
        if len(args) == 1 and isinstance(args[0], str) and ('==' in args[0] or '>' in args[0] or '<' in args[0]):
            return self.where(*args)
        # --- CASO: Valor individual T(4, 'age') ---
        # Si pides una fila y una columna, te damos el VALOR, no el cuadro.
        if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], str):
            real_col = self.gfield(args[1])
            return df.at[args[0], real_col]

        # --- CASO: Rango con ":" ---
        if len(args) >= 3 and args[1] == ":":
            start, end = args[0], args[2]
            rows = slice(start, end + 1)
            # Aquí usamos gfield para limpiar los nombres de columnas
            cols = [self.gfield(c) for c in args[3:] if isinstance(c, str)]
            
            if not cols:
                return easypandas(df.iloc[rows])
            return easypandas(df.iloc[rows][cols])

        # --- CASO: Selección mixta (procesar todos los strings con gfield) ---
        rows = []
        cols = []
        for arg in args:
            if isinstance(arg, int):
                rows.append(arg)
            elif isinstance(arg, str) and arg != ":":
                cols.append(self.gfield(arg)) # <--- ¡MAGIA AQUÍ!
        
        if rows and cols:
            return easypandas(df.iloc[rows][cols])  


   
        
        # Case 1: No arguments
        if len(args) == 0:
            return df
        
        # 🆕 Case: P(start, ":", end) or P(start, ":", end, col1, col2)
        if len(args) >= 3 and args[1] == ":" and isinstance(args[0], int) and isinstance(args[2], int):
            start, end = args[0], args[2]
            rows = slice(start, end + 1)
            cols = [c for c in args[3:] if isinstance(c, str) and c != ":"]
            
            if not cols:
                return df.iloc[rows]
            return df.iloc[rows][cols]
        
        # Case: Two strings = range by index labels
        if len(args) >= 2 and all(isinstance(a, str) for a in args[:2]):
            start, end = args[0], args[1]
            cols = [c for c in args[2:] if isinstance(c, str)]
            
            if not cols:
                return df.loc[start:end]
            return df.loc[start:end, cols]
        
        # Case 3: Single string → selection by row index or column range
        # --- REEMPLAZA DESDE AQUÍ ---
        operators = ['==', '!=', '>', '<', '>=', '<=']
        
        if len(args) == 1 and isinstance(args[0], str) and any(op in args[0] for op in operators):
            return self.where(*args)
        # --- HASTA AQUÍ ---
            
            # If it's a column range (e.g., "A:D")
            if ":" in arg:
                c1, c2 = arg.split(":")
                return df.loc[:, c1:c2]
            
            # If it's a row index (string)
            try:
                return df.loc[[arg]]
            except KeyError:
                raise ValueError(f"Index '{arg}' not found")
        
        # Case 4: Single integer → specific row
        if len(args) == 1 and isinstance(args[0], int):
            return df.iloc[[args[0]]]
        
        # Case 5: Multiple integers → multiple rows
        if all(isinstance(a, int) for a in args):
            return df.iloc[list(args)]
        
        # Case 6: Single list → multiple rows
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            return df.iloc[list(args[0])]
        
        # Case 7: Two or more arguments (rows, then columns)
        if len(args) >= 2:
            # Process rows: P(row, ":")
            if isinstance(args[0], int) and len(args) == 2 and args[1] == ":":
                return df.iloc[[args[0]]]
            
            # Process rows: P(start, end, ...) for integers
            if isinstance(args[0], int) and isinstance(args[1], int):
                start, end = args[0], args[1]
                rows = slice(start, end + 1)  # inclusive
                rest = args[2:]
            else:
                # Try to separate rows (ints) from columns (strings)
                rows = []
                cols = []
                for arg in args:
                    if isinstance(arg, int):
                        rows.append(arg)
                    elif isinstance(arg, str) and arg != ":":
                        cols.append(arg)
                
                if rows and cols:
                    return df.iloc[rows][cols]
                if rows:
                    return df.iloc[rows]
                
                raise ValueError("Invalid row format. Use: P(start, end, col1, col2, ...)")
            
            # Process columns
            if len(rest) == 0:
                return df.iloc[rows]
            
            if len(rest) == 1 and rest[0] == ":":
                return df.iloc[rows]
            
            cols = list(rest)
            for col in cols:
                if col not in df.columns:
                    raise ValueError(f"Column '{col}' not found")
            
            return df.iloc[rows][cols]
        
        # If we get here, format not recognized
        raise ValueError(f"Unrecognized format for __call__ with arguments: {args}")

    # ---------------------------------
    # Basic info
    # ---------------------------------
    @property
    def obj(self):
        return self.df
 
 
    def qty(self, mode=None):
        """
        Returns the number of records in the current selection.
        Supports 'NaN' mode for bad records detection.
        """
        if mode == 'NaN':
            # Convertimos a string y usamos el accesor .str para limpiar y comparar
            # Esto funciona columna por columna de forma segura
            bad_values = ['nan', 'none', 'null', '']
            
            # Creamos una máscara booleana: True si encuentra un malcriado
            mask = self.df.astype(str).apply(lambda col: 
                col.str.lower().str.strip().isin(bad_values)
            ).any(axis=1)
            
            return int(mask.sum())
            
        return len(self.df)

    
    def columns(self):
        return self.fields()
        
    def fields(self):
        """
        Return the list of column names.

        Example
        -------
        P.fields()
        """
        return list(self.df.columns)
    def indexlist(self):
        return self.df.index.tolist()
    # ---------------------------------
    # Show data
    # ---------------------------------

    def show(self, n=5):
        """
        Show the first n rows.

        Example
        -------
        P.show()
        P.show(10)
        """
        return self.df.head(n)

    def end(self, n=5):
        """
        Show the last n rows.

        Example
        -------
        P.end()
        """
        return self.df.tail(n)

    # ---------------------------------
    # Filtering
    # ---------------------------------

    def where(self, condition, *args, **kwargs):
        """
        Filter rows and select columns/rows in one go.
        
        AUTO-DETECTION MAGIC:
        - Strings → column names
        - Integers → row numbers  
        - ":" → all rows/all columns (optional)
        
        PARAMETERS
        ----------
        condition : str
            Filter condition (e.g., "age > 30", "city == 'Madrid'")
        *args : mixed
            Column names (str) and/or row numbers (int)
        
        RETURNS
        -------
        DataFrame with filtered results
        
        EXAMPLES
        --------
        # Basic filter
        B.where("height > 215")
        
        # Filter + specific columns
        B.where("height > 215", "name", "height")
        
        # Filter + row range (rows 0 to 10)
        B.where("height > 215", 0, 10)
        
        # Filter + range + columns
        B.where("height > 215", 0, 10, "name", "height")
        
        # Filter + specific rows
        B.where("height > 215", 0, 1, 5, "name")
        
        # Multiple conditions
        B.where("height > 215 and weight < 100")
        B.where("country == 'USA' or country == 'Canada'")
        
        # With string search
        B.where("name.str.contains('John')")
        """
 
 
        # PASO 1: Extraer el parámetro mágico 'qty' (si el usuario lo puso)
        target_qty = kwargs.get('qty', None)
        
        # PASO 2: Traducir la condición (nulos humanos a .isna())
        condicion_limpia = self._limpiar_condicion(condition)
        
        # --- PASO 3: Lógica "Whatever" y Filtro Inteligente con Salvavidas ---
        check_whatever = condicion_limpia.lower().replace(" ", "")
        
        if "whatever.isna()" in check_whatever:
            # Lógica para encontrar nulos en cualquier parte del DataFrame
            conteo_nulos = self.df.isna().sum(axis=1)
            
            if target_qty is not None:
                # Filtrar exactamente por la cantidad de nulos pedida (ej: qty=2)
                mask = (conteo_nulos == target_qty)
            else:
                # Si no hay qty, buscamos filas con al menos un nulo
                mask = (conteo_nulos > 0)
            df = self.df[mask]
            
        else:
            # Filtro normal con protección para errores de sintaxis humana (como en la imagen)
            try:
                # Intento 1: El query estándar de Pandas (rápido)
                df = self.df.query(condicion_limpia)
            except Exception:
                try:
                    # Intento 2: EL SALVAVIDAS
                    # Si el usuario puso 'Sex==Male' sin comillas, esto lo rescata
                    # Buscamos la 'condicion' original como texto en todas las filas
                    mask = self.df.astype(str).apply(
                        lambda x: x.str.contains(condition, case=False, na=False)
                    ).any(axis=1)
                    df = self.df[mask]
                except:
                    # Intento 3: Si todo falla, devolvemos el DF completo para no detener el flujo
                    df = self.df

        # PASO 4: Procesar *args (Selección inteligente de Columnas y Filas)
        columns = self.fields()
        show_cols = []
        row_nums = []
        
        for arg in args:
            if isinstance(arg, str) and arg in columns:
                show_cols.append(arg) # Es nombre de columna
            elif isinstance(arg, int):
                row_nums.append(arg)   # Es número de fila
        
        # PASO 5: Aplicar recortes y devolver resultado
        if row_nums:
            if len(row_nums) == 2:
                df = df.iloc[row_nums[0] : row_nums[1] + 1] # Rango
            else:
                df = df.iloc[row_nums] # Específicas
                
        if show_cols:
            df = df[show_cols] # Columnas seleccionadas
            
        return self.__class__(df)

    # ---------------------------------
    # Statistics
    # ---------------------------------

    def mean(self, field=None):
        """
        Compute the mean of numeric columns.

        Parameters
        ----------
        field : str (optional)
            If provided returns the mean of a specific column.

        Example
        -------
        P.mean()
        P.mean("age")
        """

        if field:
            return float(self.df[field].mean())

        df_num = self.df.select_dtypes(include=[np.number])
        means = df_num.mean()

        return list(means.index), list(means.values)
        
    def  typedata(self,*args):
        """
        Compute the type of   columns.

        Example
        -------
        P.typedata()
        P.typedata("age")
        """
        df=self.obj
        L=self.columns()
        if len(args)==0:
            return [df[data].dtype.type.__name__ for data in L]
        else:
            data = args[0]
            return df[data].dtype.type.__name__
            
    def count(self, field):
        """
        Count occurrences of values in a column.

        Example
        -------
        P.count("city")
        """
        field=self.gfield(field)
        return self.df[field].value_counts().to_dict()
    def subclases(self,field):
        field=self.gfield(field)
        return self.unique(field)
    def qtyclases(self,field):
        field=self.gfield(field)
        return len(self.unique(field))
        
    def unique(self, field):
        """
        Return unique values from a column.

        Example
        -------
        P.unique("city")
        """
        mfield=self.gfield(field)
        return list(self.df[mfield].unique())

    def top(self, field, n=5):
        """
        Return the most frequent values in a column.

        Example
        -------
        P.top("city",3)
        """
        field=self.gfield(field)
        return self.df[field].value_counts().head(n)

    # ---------------------------------
    # Index management
    # ---------------------------------

    def setindex(self, field):
        """
        Set a column as the index.

        Example
        -------
        P.setindex("name")
        """
        field=self.gfield(field)
        self.df = self.df.set_index(field)

    def resetindex(self):
        """
        Reset the index to the default numeric index.

        Example
        -------
        P.resetindex()
        """
        self.df = self.df.reset_index()

    # ---------------------------------
    # Dataset overview
    # ---------------------------------

    def summary(self):
        """
        Display a quick overview of the dataset.

        Shows number of rows, columns and simple statistics.

        Example
        -------
        P.summary()
        """

        rows = len(self.df)
        cols = len(self.df.columns)

        print("rows:", rows)
        print("fields:", cols)
        print()

        for col in self.df.columns:

            series = self.df[col]

            if pd.api.types.is_numeric_dtype(series):

                mean = round(series.mean(), 2)

                print(col, " numeric  mean:", mean)

            else:

                uniq = series.nunique()

                print(col, " text  unique:", uniq)

    def random(self, n=5, seed=None):
        """
        Return n random rows from the dataset.
        
        Parameters
        ----------
        n : int, default=5
            Number of random rows
        seed : int, optional
            Random seed for reproducible results
        
        Examples
        --------
        >>> P.random()        # 5 random rows
        >>> P.random(3)       # 3 random rows
        >>> P.random(10, 42)  # 10 rows with seed
        """
        if seed is not None:
            np.random.seed(seed)
        
        n = min(n, len(self.df))
        indices = np.random.choice(len(self.df), size=n, replace=False)
        return self.df.iloc[sorted(indices)]
    
    # ---------------------------------
    # Sorting (súper útil para estudiantes)
    # ---------------------------------
    
    def sort(self, field, ascending=True):
        """
        Sort dataframe by a column.
        
        Parameters
        ----------
        field : str
            Column name to sort by
        ascending : bool, default=True
            True for ascending, False for descending
        
        Examples
        --------
        >>> P.sort("age")           # Sort by age (youngest first)
        >>> P.sort("salary", False) # Sort by salary (highest first)
        """
        field=self.gfield(field)
        self.df = self.df.sort_values(by=field, ascending=ascending)
        return self.df
    
    # ---------------------------------
    # Basic info (para que no usen info() a ciegas)
    # ---------------------------------
    
    def info(self):
        """
        Display concise summary of the dataframe.
        
        Shows: number of rows, columns, data types, and memory usage.
        
        Example
        -------
        >>> P.info()
        """
        print(f"Dataset: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        print("\nColumn types:")
        for col in self.df.columns:
            dtype = self.df[col].dtype
            non_null = self.df[col].count()
            print(f"  {col:20} {str(dtype):15} {non_null} non-null values")
    
    # ---------------------------------
    # Rename columns (common student need)
    # ---------------------------------
    
    def rename(self, *args, **kwargs):
        """
        Rename columns in a flexible way.
    
        Examples:
        --------
        P.rename("old", "new")
        P.rename(old="new")
        P.rename(col1="new1", col2="new2")
        """
        
        # Case 1: rename("old", "new")
        if len(args) == 2:
            old, new = args
            mapping = {old: new}
        
        # Case 2: rename(col="new")
        elif kwargs:
            mapping = kwargs
        
        else:
            raise ValueError("Invalid rename usage")
        
        self.df = self.df.rename(columns=mapping)
         
    
    # ---------------------------------
    # Drop column (safe version)
    # ---------------------------------
    
    def drop(self, field):
        """
        Remove a column from the dataset.
        
        Parameters
        ----------
        field : str
            Column name to remove
        
        Example
        -------
        >>> P.drop("temp_column")
        """
        field=self.gfield(field)
        if field not in self.df.columns:
            raise ValueError(f"Column '{field}' not found")
        
        self.df = self.df.drop(columns=[field])
        return self.df
    
    # ---------------------------------
    # Fill missing values (for real datasets)
    # ---------------------------------
    
    def fillna(self, value, field=None):
        """
        Fill missing values with a specific value.
        
        Parameters
        ----------
        value : any
            Value to fill missing data with
        field : str, optional
            If provided, fill only that column
        
        Examples
        --------
        >>> P.fillna(0)              # Fill all missing with 0
        >>> P.fillna("Unknown", "city")  # Fill missing in 'city' column
        """
        if field:
            self.df[field] = self.df[field].fillna(value)
        else:
            self.df = self.df.fillna(value)
        return self.df
    
    # ---------------------------------
    # Value counts (beautiful display)
    # ---------------------------------
    
    def freq(self, field, n=10):
        """
        Show frequency count of values in a column.
        
        Parameters
        ----------
        field : str
            Column name
        n : int, default=10
            Number of top values to show
        
        Example
        -------
        >>> P.freq("city", 5)  # Top 5 cities
        """
        field=self.gfield(field)
        counts = self.df[field].value_counts().head(n)
        
        print(f"\n📊 Frequency for '{field}':")
        print("-" * 30)
        for value, count in counts.items():
            print(f"  {str(value):20} {count:>6}")
        print("-" * 30)
        print(f"  Total unique: {self.df[field].nunique()}")
        
        return counts
    
    # ---------------------------------
    # Min and Max (basic stats)
    # ---------------------------------
    
    def min(self, field):
        """
        Return minimum value in a column.
        
        Example
        -------
        >>> P.min("age")
        """
        field=self.gfield(field)
        return self.df[field].min()
    
    def max(self, field):
        """
        Return maximum value in a column.
        
        Example
        -------
        >>> P.max("age")
        """
        field=self.gfield(field)
        return self.df[field].max()

    def values(self, *args):
        """
        Get RAW values cleaned of NumPy types with flexible arguments.
        """
        # Internal helper for native Python types
        def clean(val):
            if hasattr(val, 'item'): val = val.item()
            if isinstance(val, float) and val.is_integer(): return int(val)
            return val

        # 1. Handle P.values() -> Full DataFrame
        if not args:
            data = self.df.values.tolist()
            return [[clean(cell) for cell in row] for row in data]

        # 2. Extract context using loc/iloc through your __call__ logic
        # We use a trick: P(*args) already returns the right Grid/DataFrame
        result = self(*args)

        # 3. Process the result based on what P(*args) returned
        
        # If it's a single value (Scalar)
        if not hasattr(result, "__len__") or isinstance(result, (int, float, str)):
            return clean(result)

        # If it's a Series (Single row or Single Column)
        if isinstance(result, pd.Series):
            return [clean(x) for x in result.tolist()]

        # If it's a DataFrame (Block of data)
        if isinstance(result, pd.DataFrame):
            raw_list = result.values.tolist()
            # If the result is just one row (e.g., P.values(3))
            if len(raw_list) == 1:
                return [clean(x) for x in raw_list[0]]
            # Multiple rows
            return [[clean(cell) for cell in row] for row in raw_list]

        return result

    
    def row_data(self, row):
        """
        Get row as dictionary (column: value)
        
        Example
        --------
        >>> P.row_data(0)
        {'Day': 'Monday', 'Coffee Type': 'Espresso', 'Units Sold': 25}
        """
        return self(row).iloc[0].to_dict()
    
    def cell(self, row, col):
        """
        Get a single cell value.
        
        Example
        --------
        >>> P.cell(0, "Units Sold")  # 25
        >>> P.cell(0, 2)             # 25 (by position)
        """
        return self.values(row, col)

 
    
    def assign(self, *args, show=False):
        """
        Assign values safely to the DataFrame.
        
        Parameters
        ----------
        *args : tuple
            Formatos: (start, end, column, value) o (rows, column, value)
        show : bool, default=False
            If True, returns the modified DataFrame (for quick preview)
        
        Examples
        --------
        >>> C.assign(1, 3, "Units Sold", 10)  # Silent assignment
        >>> C.assign(1, 3, "Units Sold", 10, show=True)  # Returns DataFrame
        """
        df = self.df
        
        # Parse arguments
        if len(args) == 4 and isinstance(args[0], int) and isinstance(args[1], int):
            start, end, column, value = args
            df.loc[start:end, column] = value
            
        elif len(args) == 3 and isinstance(args[0], list):
            rows, column, value = args
            df.loc[rows, column] = value
            
        elif len(args) == 3 and isinstance(args[0], str):
            row_label, column, value = args
            df.loc[row_label, column] = value
            
        else:
            raise ValueError("Invalid assign format. Use: assign(start, end, column, value)")
        
        # Show if requested
        if show:
            # Mostrar solo las filas afectadas (si son pocas)
            if len(args) >= 2 and isinstance(args[0], int) and isinstance(args[1], int):
                # Range assignment - show the modified range
                start, end = args[0], args[1]
                print(f"✅ Assigned {value} to '{column}' (rows {start}-{end})")
                return self(start, end)  # Reuse __call__ to show affected rows
            elif len(args) >= 2 and isinstance(args[0], list):
                rows = args[0]
                print(f"✅ Assigned {value} to '{column}' (rows {rows})")
                if len(rows) <= 10:  # Only show if reasonable number
                    return self(*rows)  # Show specific rows
                else:
                    return self.df.head()  # Show head instead
            else:
                print(f"✅ Assigned {value} to '{column}'")
                return self.df.head()
        
        return self  # For chaining
    
    # Versión más simple para estudiantes

    def set(self, column, value, condition=None):
        """
        Updates or modifies a column based on a value or a mathematical expression.
        Supports conditional updates and case-insensitive column mapping.
    
        Parameters:
        -----------
        column : str
            The name of the column to be modified.
        value : str, int, or float
            The new value or a string expression (e.g., 'Age * 2').
        condition : str, optional
            A string-based logical condition to filter rows (e.g., 'Age > 18').
    
        Examples:
        ---------
        >>> # 1. Simple global update
        >>> P.set("Age", "Age + 1")
        
        >>> # 2. Conditional value update
        >>> P.set("Color", "Blue", "Color == 'Green'")
        
        >>> # 3. Targeted numerical reset
        >>> P.set("Factor", 0, "Age < 3")
        
        >>> # 4. Complex math with conditions
        >>> P.set("Factor", "Factor * 1.5", "Sex == 'M'")
        """
        # 1. Column existence validation (Case-insensitive mapping)
        column = self.gfield(column)
        col_map = {c.lower(): c for c in self.df.columns}
        target_col = col_map.get(column.lower(), column) 
        
        affected_rows = 0 # Inicializamos el contador

        if condition:
            # Get boolean mask for the condition
            mask = self.df.eval(condition)
            affected_rows = mask.sum() # Contamos cuántos True hay en la máscara
            
            if affected_rows > 0:
                # Check if value is a math expression
                if isinstance(value, str) and any(op in value for op in "+-*/"):
                    self.df.loc[mask, target_col] = self.df.eval(value)
                else:
                    self.df.loc[mask, target_col] = value
        else:
            # Global operation on the entire column
            affected_rows = len(self.df) # Si no hay condición, se afecta toda la columna
            if isinstance(value, str) and any(op in value for op in "+-*/"):
                self.df[target_col] = self.df.eval(value)
            else:
                self.df[target_col] = value
                
        # Mensaje mucho más informativo para tu Capítulo 5
        print(f"✅ Column '{target_col}' updated. Rows affected: {affected_rows}")
     
    def fillnan(self, field, value, *args):
        # Si hay argumentos en *args, el primero es nuestra condición
        # Pero le sumamos automáticamente la detección de NaNs
        
        if args:
            # Combinamos la condición del usuario con la detección de nulos
            # Usamos 'and' para que solo actúe donde se cumplan AMBAS
            user_condition = args[0]
            full_condition = f"({user_condition}) and ( {field} != {field} )"
        else:
            # Si no hay args, solo buscamos nulos en esa columna
            full_condition = f"{field} != {field}"
        
        # Reutilizamos tu función set que ya cuenta filas
        return self.set(field, value, full_condition)

        
    def multiset(self, column, labels, conditions, default="Other"):
        """
        Applies multiple conditions to a single column in one go.
        
        Example:
        P.multiset("Generation", 
                   ["Baby", "Child", "Adult"], 
                   ["Age < 3", "Age >= 3 and Age < 18", "Age >= 18"])
        """
        # 1. Asegurarnos de que la columna existe (si no, la creamos)
        if column not in self.df.columns:
            self.df[column] = default
    
        # 2. Convertir los strings de condiciones en máscaras booleanas
        masks = [self.df.eval(cond) for cond in conditions]
    
        # 3. Aplicar la lógica de selección múltiple
        self.df[column] = np.select(masks, labels, default=self.df[column])
        
        print(f"🧬 Multiset applied to '{column}' with {len(labels)} categories.")
        
    def cell(self, row, col):
        """
        Get a single cell value (fast, scalar access).
        
        Parameters
        ----------
        row : int or str
            Row position (int) or row label (str if index is set)
        col : int or str
            Column position (int) or column name (str)
        
        Returns
        -------
        Single value (scalar)
        
        Examples
        --------
        >>> C.cell(3, 1)              # Row 3, column at position 1
        >>> C.cell(3, "Units Sold")   # Row 3, column by name
        >>> C.cell("Monday", "Units Sold")  # By index label (after setindex)
        """
        df = self.df
        
        # Case 1: Both are integers (position-based, fastest)
        if isinstance(row, int) and isinstance(col, int):
            return df.iat[row, col]
        
        # Case 2: Row int, col string (position + column name)
        if isinstance(row, int) and isinstance(col, str):
            return df.iloc[row][col]
        
        # Case 3: Row string, col string (label-based, after setindex)
        if isinstance(row, str) and isinstance(col, str):
            return df.loc[row, col]
        
        # Case 4: Row string, col int (label + position)
        if isinstance(row, str) and isinstance(col, int):
            return df.loc[row, df.columns[col]]
        
        raise ValueError(f"Invalid cell access: row={row}, col={col}")
    
    # Versión rápida para cuando solo quieres el valor sin verificación
    def fast_cell(self, row, col):
        """Faster cell access when you know both are integers"""
        return self.df.iat[row, col]

    def join(self, other, left=None, right=None, on=None, how="inner"):
        
        # Get underlying DataFrame
        other_df = getattr(other, "df", other)
    
        if on is not None:
            df = self.df.merge(other_df, on=on, how=how)
        else:
            df = self.df.merge(other_df, left_on=left, right_on=right, how=how)
        
        return easypandas(df)

    def append(self, other):
        """
        Append another dataset (row-wise).
        
        Example:
        --------
        A.append(B)
        """
        other_df = getattr(other, "df", other)
        
        df = pd.concat([self.df, other_df], ignore_index=True)
        
        return easypandas(df)

    def interpolate(self, field):
        field=self.gfield(field)
        """
        Fill missing values using interpolation.
        
        Example:
        --------
        C.interpolate("Units Sold")
        """
        self.df[field] = self.df[field].interpolate()
        return self
 
        
 

    def gfield(self, sexpr):
        """
        Normalizes column names in simple strings or logical expressions.
        Example: gfield("coLor=='red'") -> "Color=='red'"
        """
        L = self.columns()
        lookup = {x.lower(): x for x in L}
    
        # 1. Si es un nombre de columna directo (sin operadores)
        if sexpr.lower() in lookup:
            return lookup[sexpr.lower()]
    
        # 2. Si es una expresión (ej: "coLor=='red'"), buscamos la palabra clave
        # Esta regex busca la primera palabra antes de un operador o espacio
        match = re.match(r'^([a-zA-Z0-9_]+)', sexpr)
        if match:
            word = match.group(1)
            if word.lower() in lookup:
                real_name = lookup[word.lower()]
                # Reemplazamos la versión mal escrita por la real
                return sexpr.replace(word, real_name, 1)
    
        return sexpr
 
    def datagrid(self, col_filters, row_filters, col_names=None, row_names=None, title="Survival Analysis %"):
        import pandas as pd
        import matplotlib.pyplot as plt
        
        # 1. Etiquetas y Matrix (Tu lógica impecable)
        c_names = col_names if col_names else col_filters
        r_names = row_names if row_names else row_filters
        
        matrix = []
        for r_f in row_filters:
            row_data = []
            for c_f in col_filters:
                combined = f"({r_f}) and ({c_f})"
                count = len(self.where(combined).df) 
                row_data.append(count)
            matrix.append(row_data)
        
        df_grid = pd.DataFrame(matrix, index=r_names, columns=c_names)
        
        # 2. Porcentajes para el gráfico
        df_perc = df_grid.div(df_grid.sum(axis=1), axis=0) * 100
    
        # --- GRÁFICO COMPACTO (MITAD DE ALTURA) ---
        # Cambiamos figsize a (10, 3) para que sea bajito y ancho
        ax = df_perc.plot(kind='barh', stacked=True, figsize=(10, 3), color=['#2ecc71', '#e74c3c'])
        
        plt.title(title, fontsize=12, fontweight='bold', pad=15)
        plt.xlabel("Percentage (%)")
        plt.xlim(0, 100)
        
        # Etiquetas de % dentro de las barras
        for p in ax.patches:
            width = p.get_width()
            if width > 1:
                ax.text(p.get_x() + width/2, p.get_y() + p.get_height()/2, 
                        f'{int(width)}%', va='center', ha='center', 
                        color='white', fontweight='bold', fontsize=10)
        
        # Ajustamos la leyenda para que no estorbe
        plt.legend(title="Status", loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        plt.show()
    
        # 3. La Tabla de salida (Totales)
        df_final = df_grid.copy()
        df_final['Total'] = df_final.sum(axis=1)
        df_final.loc['Total'] = df_final.sum(axis=0)
        
        return easypandas(df_final)

    def getnulls(self, columna=None):
        """
        Si pasas una columna, te da las filas con NaN en esa columna.
        Si no pasas nada, te da las filas que tengan AL MENOS un NaN en cualquier parte.
        """
        if columna:
            # Filtro específico
            mask = self.df[columna].isna()
        else:
            # Filtro global
            mask = self.df.isna().any(axis=1)
            
        return self.__class__(self.df[mask])
        
    def fix(self, columna, nuevo_valor, condicion, *args):
        condicion = self._limpiar_condicion(condicion)
        # 1. Aplicar el cambio principal
        
        idx_cumple = self.where(condicion).df.index
        self.df.loc[idx_cumple, columna] = nuevo_valor
        
        # 2. Si hay argumentos extra, detectamos qué son
        if args:
            idx_no_cumple = self.df.index.difference(idx_cumple)
            sub_df = self.df.loc[idx_no_cumple]
            
            # Variables para el ELSE / ELSE IF
            valor_final = None
            condicion_extra = None
            
            for arg in args:
                # Si el argumento tiene símbolos lógicos, es una CONDICIÓN
                if isinstance(arg, str) and any(op in arg for op in ['>', '<', '==', '!=', '.isna']):
                    condicion_extra = arg
                else:
                    # Si es un número o un string plano, es un VALOR
                    valor_final = arg

            # LÓGICA DE APLICACIÓN
            if condicion_extra and valor_final is not None:
                # Caso: ELSE IF (cumple la nueva condición)
                idx_else_if = sub_df.query(condicion_extra).index
                self.df.loc[idx_else_if, columna] = valor_final
            elif valor_final is not None:
                # Caso: ELSE (no hubo condición extra, solo un valor final)
                self.df.loc[idx_no_cumple, columna] = valor_final
                
        return self 
        
    def family(self, column_name):
        column_name=self.gfield(column_name)
        """
        Explora la identidad de una columna. 
        Si tiene categorías, muestra los integrantes. 
        Si es un dato continuo, devuelve su tipo técnico.
        """
        from rich.console import Console
        from rich.panel import Panel
        from rich.columns import Columns
        
        console = Console()
        col = self.df[column_name]
        
        # 1. Identificar la naturaleza del dato
        # Si es flotante o si casi todos los valores son únicos (poca repetición = no es familia)
        if col.dtype == 'float64':
            console.print("[bold yellow]float[/bold yellow]")
            return
            
        if col.dtype == 'int64' and col.nunique() > len(col) * 0.5:
            # Si son muchos enteros distintos (como un ID o Contador), no es familia
            console.print("[bold yellow]int[/bold yellow]")
            return
    
        # 2. Si pasó los filtros, es una familia (Categorías)
        # Obtenemos los únicos y los convertimos a string para visualización
        members = col.unique().tolist()
        
        # Ordenar un poco para que no sea un caos (opcional)
        try:
            members.sort(key=lambda x: (x is None, str(x)))
        except:
            pass
    
        # Crear los paneles visuales
        member_panels = [
            Panel(str(m), expand=True, border_style="cyan") 
            for m in members
        ]
        
        console.print(f"\n[bold magenta]👨‍👩‍👧‍👦 Family of '{column_name}':[/bold magenta]")
        console.print(Columns(member_panels))
     
     

 

    def summary(self):
        console = Console()
        
        # Configuramos la tabla con rejilla y filas alternas
        table = Table(
            title="🔍 easypandas DATA HEALTH CHECK", 
            title_style="bold magenta",
            show_header=True,
            header_style="bold white on blue",
            row_styles=["none", "dim"], 
            show_lines=True, 
            box=None
        )

        # Todas las columnas justificadas a la izquierda (left)
        table.add_column("FEATURE", justify="left", style="bold cyan", no_wrap=True)
        table.add_column("TYPE", justify="left", style="bold yellow")
        table.add_column("QTY CAT", justify="left", style="bold")
        table.add_column("SAMPLE DATA", justify="left", style="") 
        table.add_column("OK", justify="left", style="bold blue")
        table.add_column("NaNs", justify="left", style="bold red")

        for col in self.df.columns:
            # Obtenemos los datos limpios de sniffdata
            stype, example, ok, nans, qcat = self.sniffdata(col)
            
            table.add_row(
                str(col).upper(), 
                stype.upper(), 
                str(qcat), 
                str(example), 
                str(ok), 
                str(nans)
            )

        console.print(table) 
        
    def sniffdata(self, ncolumn):
        ncolumn=self.gfield(ncolumn)
        col = self.df[ncolumn]
        total = len(col)
        non_nan = col.count()
        nans = total - non_nan
        unique_vals = col.unique()
        n_unique = len(unique_vals)
        
        qty_cat = "" # Por defecto vacío
        
        if pd.api.types.is_numeric_dtype(col):
            if n_unique == total and (col.dropna().diff().iloc[1:] == 1).all():
                stype = "autonumeric"
                example = f"{col.iloc[0]}...{col.iloc[-1]}"
            elif pd.api.types.is_integer_dtype(col):
                stype = "integer"
                example = [int(x) for x in col.dropna().head(3).tolist()]
            else:
                stype = "float"
                example = [float(x) for x in col.dropna().head(2).tolist()]
                
        elif n_unique < (total * 0.1): 
            stype = "categories"
            example = [str(x) for x in unique_vals[:4]]
            qty_cat = int(n_unique) # Solo aquí llenamos el valor
        else:
            stype = "string"
            example = [str(x) for x in col.dropna().head(2).tolist()]

        return [stype, example, int(non_nan), int(nans), qty_cat]   

 

    def _limpiar_condicion(self, condicion):
        """
        Escanea la condición buscando nombres de columnas y los 
        normaliza usando gfield sin romper la lógica de Python.
        """
        # 1. Obtenemos el mapa de traducción (nuestro gfield atómico)
        columnas_reales = self.columns()
        lookup = {x.lower(): x for x in columnas_reales}
        
        # 2. Buscamos "palabras" en la condición
        # Este regex busca palabras que no estén entre comillas
        palabras = re.findall(r'\b\w+\b', condicion)
        
        nueva_condicion = condicion
        for p in palabras:
            p_low = p.lower()
            # Si la palabra coincide con una columna (ignorando mayúsculas)
            if p_low in lookup and p != lookup[p_low]:
                # La reemplazamos por la versión real de gfield
                # Usamos regex para reemplazar solo la palabra exacta (\b)
                nueva_condicion = re.sub(rf'\b{p}\b', lookup[p_low], nueva_condicion)
                
        return nueva_condicion  

    def cleanNaN(self):
        initial_qty = self.qty()
        
        # Misma lógica corregida:
        bad_values = ['nan', 'none', 'null', '']
        mask = self.df.astype(str).apply(lambda col: 
            col.str.lower().str.strip().isin(bad_values)
        ).any(axis=1)
        
        # Filtramos: nos quedamos con lo que NO está en la máscara (~)
        self.df = self.df[~mask].dropna()
        
        final_qty = self.qty()
        removed = initial_qty - final_qty
        
        from rich.console import Console
        console = Console()
        if removed > 0:
            console.print(f"\n[bold red]🚀 flush  flush  !!![/bold red]  {removed} bad records removed.")
        else:
            console.print("[yellow] Nothing to delete. Data is already crystal clear.[/yellow]")
            
        return self

    def saveas(self, filename="output.csv"):
            """
            The Swiss Army Knife of saving. 
            Now defaults to .csv for speed and compatibility.
            Supports .xlsx, .csv, .txt and .pdf.
            """
            from rich.console import Console
            console = Console()
            
            # Si el usuario no puso extensión, le ponemos la de por defecto (.csv)
            if '.' not in filename:
                filename += ".csv"
                
            try:
                # 1. CSV (The new default king)
                if filename.endswith('.csv'):
                    self.df.to_csv(filename, index=False)
                
                # 2. Excel
                elif filename.endswith('.xlsx'):
                    self.df.to_excel(filename, index=False)
                
                # 3. Plain Text
                elif filename.endswith('.txt'):
                    with open(filename, 'w') as f:
                        f.write(self.df.to_string(index=False))
                
                # 4. PDF (The snapshot)
                elif filename.endswith('.pdf'):
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(12, 4))
                    ax.axis('tight')
                    ax.axis('off')
                    table = ax.table(cellText=self.df.head(20).values, 
                                    colLabels=self.df.columns, 
                                    cellLoc='center', loc='center')
                    plt.savefig(filename)
                    plt.close()
    
                console.print(f"\n[bold green]✔ Mission Accomplished![/bold green] Saved as: [cyan]{filename}[/cyan]")
            
            except Exception as e:
                console.print(f"\n[bold red]✘ Save failed:[/bold red] {str(e)}")
                
            return self


    def familyfield(self):
        L=self.columns()
        vec=[]
        for data in L:
            k=self.sniffdata(data)
            if k[0]=='categories':
                vec.append(data)
        if len(vec)==1:
            return vec[0]
        else:    
            return vec

    def insertcolumn(self, name, value=0, pos=None):
        """
        Inserts a new column at a specific position (left-side) or at the end.
        
        Example:
        P.insertcolumn("Generation", "Other", pos=0) # Makes it the FIRST column (leftmost)
        """
        # Verificamos si la columna ya existe para evitar errores de Pandas
        if name in self.df.columns:
            print(f"⚠️ Column '{name}' already exists. Use set() to modify it.")
            return
    
        if pos is None:
            self.df[name] = value
        else:
            # Aseguramos que pos no sea mayor al número de columnas actual
            max_pos = len(self.df.columns)
            actual_pos = min(pos, max_pos)
            self.df.insert(actual_pos, name, value)
            
        print(f"🆕 Column '{name}' inserted at position {pos if pos is not None else 'end'}.")        

    #******************************#        
    #***         Ploting        ***#
    #******************************# 

    
    def familystat(self, column):
        # Llamamos a la función de la otra librería pasando nuestro df interno
        return familystat(self.df, column) 
        
    def superedit(self, *args):
        import dtale
        
        # 1. Si no hay argumentos, mostramos todo como antes
        if not args:
            return dtale.show(self.df)
        
        # 2. Si hay argumentos, usamos la lógica de tu función 'where'
        # para obtener solo la "rebanada" de datos que nos interesa
        filtered_data = self.where(*args)
        
        # 3. Lanzamos dtale pero solo con el DataFrame filtrado (.df)
        print(f"Opening SuperEdit for: {args}")
        return dtale.show(filtered_data.df)
 
 
    def generalplot(self):
        from easyplot import generalplot
        return generalplot(self.df)

    def versusplot(self, x_name, y_name, color=None, kind='scatter'):
        from easyplot import plotversus
        real_x = self.gfield(x_name)
        real_y = self.gfield(y_name)
        real_color = self.gfield(color) if color else None

        return plotversus(self.df,real_x, real_y, color=real_color, kind=kind)
           
def typename(x):
    return type(x).__name__

