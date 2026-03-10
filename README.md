# easypandas — Simple Data Exploration for Students

`easypandas` is a small educational wrapper around **pandas** that provides a simpler interface for beginners learning data analysis.

The goal is to allow students to explore datasets using simple and intuitive commands.

Internally it uses the power of **pandas**, but exposes a friendlier syntax.

---

# Creating a Dataset

Example dataset:


```python
from  lib_pandas import *

data = {
"nombre":["Ana","Luis","Pedro"],
"edad":[30,40,36],
"qty_autos":[1,2,0]
}

P = easypandas(data)
```

# Basic Exploration

## Number of rows


```python
P.qty
```




    3



## Show first rows


```python
P.show()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>nombre</th>
      <th>edad</th>
      <th>qty_autos</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Ana</td>
      <td>30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Luis</td>
      <td>40</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Pedro</td>
      <td>36</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



## Show last rows


```python
P.end()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>nombre</th>
      <th>edad</th>
      <th>qty_autos</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Ana</td>
      <td>30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Luis</td>
      <td>40</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Pedro</td>
      <td>36</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



## List columns


```python
P.fields()
```




    ['nombre', 'edad', 'qty_autos']



# Filtering Data

You can filter rows using simple expressions.


```python
P.where("edad > 30")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>nombre</th>
      <th>edad</th>
      <th>qty_autos</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Luis</td>
      <td>40</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Pedro</td>
      <td>36</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



nombre   edad   qty_autos
Luis     40     2
Pedro    36     0
```

This follows the logical expression:

$$
edad > 30
$$


```python
P.mean()
```




    (['edad', 'qty_autos'], [np.float64(35.333333333333336), np.float64(1.0)])



Mathematically the mean is defined as

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i
$$
## Mean of a specific column


```python
P.mean("edad")
```




    35.333333333333336



# Counting Values


```python
P.count("nombre")
```




    {'Ana': 1, 'Luis': 1, 'Pedro': 1}



# Unique Values


```python
P.unique("nombre")
```




    ['Ana', 'Luis', 'Pedro']



# Most Frequent Values


```python
P.top("nombre")
```




    nombre
    Ana      1
    Luis     1
    Pedro    1
    Name: count, dtype: int64



This returns the most common values in a column.

---

# Index Management

## Set a column as index


```python
P.setindex("nombre")
```

## Reset index


```python
P.resetindex()
```

# Dataset Summary


```python
P.summary()
```

    rows: 3
    fields: 3
    
    nombre  text  unique: 3
    edad  numeric  mean: 35.33
    qty_autos  numeric  mean: 1.0
    

# Mathematical Interpretation

For numeric columns, statistics are computed using common formulas.

Mean:

$$
\bar{x} = \frac{x_1 + x_2 + ... + x_n}{n}
$$

Variance:

$$
\sigma^2 = \frac{1}{n}\sum (x_i - \bar{x})^2
$$

Standard deviation:

$$
\sigma = \sqrt{\sigma^2}
$$

---

# Typical Workflow

A typical student exploration session might look like:


```python
P.summary()
```

    rows: 3
    fields: 3
    
    nombre  text  unique: 3
    edad  numeric  mean: 35.33
    qty_autos  numeric  mean: 1.0
    


```python
P.show()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>nombre</th>
      <th>edad</th>
      <th>qty_autos</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Ana</td>
      <td>30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Luis</td>
      <td>40</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Pedro</td>
      <td>36</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python
P.mean("edad")
```




    35.333333333333336




```python
P.count("nombre")
```




    {'Ana': 1, 'Luis': 1, 'Pedro': 1}




```python
P.where("edad > 30")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>nombre</th>
      <th>edad</th>
      <th>qty_autos</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Luis</td>
      <td>40</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Pedro</td>
      <td>36</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



# Philosophy

The philosophy of `easypandas` is:

* Simplicity
* Readability
* Learning before complexity

Students first explore data using simple commands, and later transition to full **pandas** functionality.



```python

```


```python

```
