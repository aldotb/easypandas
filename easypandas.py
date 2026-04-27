import pandas as pd
import numpy as np

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
        
        # Case 1: Already a DataFrame
        if isinstance(data, pd.DataFrame):
            self.pdobj = data.copy()
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
                                self.pdobj = pd.read_excel(data, engine='calamine', **kwargs)
                            except ImportError:
                                # Fallback to openpyxl if calamine not installed
                                self.pdobj = pd.read_excel(data, engine='openpyxl', **kwargs)
                        else:  # .xls old format
                            self.pdobj = pd.read_excel(data, engine='xlrd', **kwargs)
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
                    
                    self.pdobj = reader(data, **kwargs)
            else:
                raise ValueError(f"Unsupported file extension '{ext}'. Supported: {list(readers.keys())}")
            return
        
        # Case 3: All other cases (dict, list, array, etc.)
        try:
            self.pdobj = pd.DataFrame(data, **kwargs)
        except Exception as e:
            raise TypeError(
                f"Cannot create DataFrame from {type(data)}. "
                f"Supported: DataFrame, file path (str), dict, list, tuple, np.ndarray. Error: {e}"
            )  

    # ---------------------------------
    # Redirect unknown attributes to pandas
    # ---------------------------------
    def __getattr__(self, name):
        attr = getattr(self.pdobj, name)
    
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
        return repr(self.pdobj)
    
    def __str__(self):
        """Muestra el DataFrame con print()"""
        return str(self.pdobj)
    
    def __dir__(self):
        """
        Improve autocomplete: include easypandas + pandas methods
        """
        return list(set(
            dir(self.__class__) +      # métodos de easypandas
            list(self.__dict__.keys()) +
            dir(self.pdobj)            # métodos de pandas
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
        
        df = self.pdobj
        
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
        if len(args) == 1 and isinstance(args[0], str):
            arg = args[0]
            
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
    def qty(self):
        """
        Return the number of rows in the table.

        Example
        -------
        P.qty
        """
        return len(self.pdobj)

    
    def columns(self):
        return self.fields()
        
    def fields(self):
        """
        Return the list of column names.

        Example
        -------
        P.fields()
        """
        return list(self.pdobj.columns)
    def indexlist(self):
        return self.pdobj.index.tolist()
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
        return self.pdobj.head(n)

    def end(self, n=5):
        """
        Show the last n rows.

        Example
        -------
        P.end()
        """
        return self.pdobj.tail(n)

    # ---------------------------------
    # Filtering
    # ---------------------------------

    def where(self, condition, *args):
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
        
        # Step 1: Apply the filter condition
        df = self.pdobj.query(condition)
        
        # Step 2: Parse arguments
        columns = self.fields()
        show_cols = []
        row_nums = []
        
        for arg in args:
            # Case: Column name
            if isinstance(arg, str) and arg in columns:
                show_cols.append(arg)
            # Case: ":" means all (ignore, do nothing)
            elif arg == ":":
                continue
            # Case: Integer (row number)
            elif isinstance(arg, int):
                row_nums.append(arg)
            # Case: Unknown string
            elif isinstance(arg, str) and arg not in columns:
                raise ValueError(f"Column '{arg}' not found. Available: {columns}")
        
        # Step 3: Apply row selection
        if row_nums:
            if len(row_nums) == 2:
                # Range: where(..., 0, 10) → rows 0 to 10 (inclusive)
                start, end = row_nums[0], row_nums[1]
                df = df.iloc[start:end+1]
            else:
                # Multiple specific rows: where(..., 0, 1, 5)
                df = df.iloc[row_nums]
        
        # Step 4: Apply column selection
        if show_cols:
            df = df[show_cols]
        
        return easypandas(df)

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
            return float(self.pdobj[field].mean())

        df_num = self.pdobj.select_dtypes(include=[np.number])
        means = df_num.mean()

        return list(means.index), list(means.values)

    def count(self, field):
        """
        Count occurrences of values in a column.

        Example
        -------
        P.count("city")
        """
        return self.pdobj[field].value_counts().to_dict()

    def unique(self, field):
        """
        Return unique values from a column.

        Example
        -------
        P.unique("city")
        """
        return list(self.pdobj[field].unique())

    def top(self, field, n=5):
        """
        Return the most frequent values in a column.

        Example
        -------
        P.top("city",3)
        """
        return self.pdobj[field].value_counts().head(n)

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
        self.pdobj = self.pdobj.set_index(field)

    def resetindex(self):
        """
        Reset the index to the default numeric index.

        Example
        -------
        P.resetindex()
        """
        self.pdobj = self.pdobj.reset_index()

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

        rows = len(self.pdobj)
        cols = len(self.pdobj.columns)

        print("rows:", rows)
        print("fields:", cols)
        print()

        for col in self.pdobj.columns:

            series = self.pdobj[col]

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
        
        n = min(n, len(self.pdobj))
        indices = np.random.choice(len(self.pdobj), size=n, replace=False)
        return self.pdobj.iloc[sorted(indices)]
    
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
        self.pdobj = self.pdobj.sort_values(by=field, ascending=ascending)
        return self.pdobj
    
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
        print(f"Dataset: {self.pdobj.shape[0]} rows × {self.pdobj.shape[1]} columns")
        print("\nColumn types:")
        for col in self.pdobj.columns:
            dtype = self.pdobj[col].dtype
            non_null = self.pdobj[col].count()
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
        
        self.pdobj = self.pdobj.rename(columns=mapping)
        return self
    
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
        if field not in self.pdobj.columns:
            raise ValueError(f"Column '{field}' not found")
        
        self.pdobj = self.pdobj.drop(columns=[field])
        return self.pdobj
    
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
            self.pdobj[field] = self.pdobj[field].fillna(value)
        else:
            self.pdobj = self.pdobj.fillna(value)
        return self.pdobj
    
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
        counts = self.pdobj[field].value_counts().head(n)
        
        print(f"\n📊 Frequency for '{field}':")
        print("-" * 30)
        for value, count in counts.items():
            print(f"  {str(value):20} {count:>6}")
        print("-" * 30)
        print(f"  Total unique: {self.pdobj[field].nunique()}")
        
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
        return self.pdobj[field].min()
    
    def max(self, field):
        """
        Return maximum value in a column.
        
        Example
        -------
        >>> P.max("age")
        """
        return self.pdobj[field].max()


    def values(self, row, col=None):
        """
        Get RAW values (not DataFrame).
        
        Parameters
        ----------
        row : int or str
            Row number or index label
        col : str, optional
            Specific column name
        
        Examples
        --------
        >>> P.values(0)           # ['Monday', 'Espresso', 25]
        >>> P.values(0, "Units Sold")  # 25
        >>> P.values(0, 0)        # 'Monday' (by column position)
        """
        df_at_row = self(row)  # Reuse __call__
        
        if col is None:
            # Return all values as list
            return df_at_row.iloc[0].tolist()
        
        if isinstance(col, int):
            # Column by position
            return df_at_row.iloc[0, col]
        
        # Column by name
        return df_at_row[col].iloc[0]
    
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
        df = self.pdobj
        
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
                    return self.pdobj.head()  # Show head instead
            else:
                print(f"✅ Assigned {value} to '{column}'")
                return self.pdobj.head()
        
        return self  # For chaining
    
    # Versión más simple para estudiantes
    def set(self, rows, column, value):
        """
        Set values in a column for specific rows.
        
        Examples:
        --------
        C.set(1, "Units Sold", 10)           # Single row
        C.set([1,3,5], "Units Sold", 0)      # Multiple rows
        C.set(slice(1,4), "Units Sold", 10)  # Range using slice
        """
        self.pdobj.loc[rows, column] = value
        return self

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
        df = self.pdobj
        
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
        return self.pdobj.iat[row, col]

    def join(self, other, left=None, right=None, on=None, how="inner"):
        
        # Get underlying DataFrame
        other_df = getattr(other, "pdobj", other)
    
        if on is not None:
            df = self.pdobj.merge(other_df, on=on, how=how)
        else:
            df = self.pdobj.merge(other_df, left_on=left, right_on=right, how=how)
        
        return easypandas(df)

    def append(self, other):
        """
        Append another dataset (row-wise).
        
        Example:
        --------
        A.append(B)
        """
        other_df = getattr(other, "pdobj", other)
        
        df = pd.concat([self.pdobj, other_df], ignore_index=True)
        
        return easypandas(df)

    def interpolate(self, field):
        """
        Fill missing values using interpolation.
        
        Example:
        --------
        C.interpolate("Units Sold")
        """
        self.pdobj[field] = self.pdobj[field].interpolate()
        return self