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

    def __init__(self, data):
        """
        Create a new ptranslate object.

        Parameters
        ----------
        data : dict, list, or DataFrame
            Data used to create the internal table.
        """
        self.pdobj = pd.DataFrame(data)

    # ---------------------------------
    # Redirect unknown attributes to pandas
    # ---------------------------------

    def __getattr__(self, name):
        """
        Redirect unknown attributes to the internal pandas DataFrame.

        This allows access to native pandas methods like:

        P.describe()
        P.head()
        P.columns
        """
        return getattr(self.pdobj, name)

    # ---------------------------------
    # Allow column access
    # ---------------------------------

    def __getitem__(self, key):
        """
        Access a column using bracket syntax.

        Example
        -------
        P["age"]
        """
        return self.pdobj[key]

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

    def fields(self):
        """
        Return the list of column names.

        Example
        -------
        P.fields()
        """
        return list(self.pdobj.columns)

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

    def where(self, condition, newpd=False):
        """
        Filter rows using a condition.

        Parameters
        ----------
        condition : str
            Condition expression.

        newpd : bool
            If True returns a new ptranslate object.

        Example
        -------
        P.where("age > 30")
        """
        df = self.pdobj.query(condition)

        if newpd:
            return ptranslate(df)

        return df

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