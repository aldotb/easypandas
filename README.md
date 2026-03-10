````markdown
# easypandas — Simple Data Exploration for Students

`easypandas` is an educational wrapper around **pandas** that makes data exploration simpler for beginners.  

The goal is to allow students to explore datasets using **simple and intuitive commands**, while still giving access to **all pandas functionality** if needed.

---

## Creating a Dataset

```python
from lib_pandas import *

data = {
    "nombre":["Ana","Luis","Pedro","María","Carla"],
    "edad":[30,40,36,28,35],
    "qty_autos":[1,2,0,1,2]
}

P = easypandas(data)
````

Or load a dataset directly from CSV:

```python
MyLib = easypandas(df=pd.read_csv("titanic.csv"))
```

> Note: You can still use **pandas functions** like `.head()`, `.describe()`, `.groupby()`, etc.:

```python
MyLib.head()
MyLib.describe()
```

---

## Basic Exploration

### Number of rows

```python
P.qty
```

Result:

```
5
```

---

### Show first rows

```python
P.show()
```

---

### Show last rows

```python
P.end(3)
```

---

### List columns

```python
P.fields()
```

Result:

```
['nombre', 'edad', 'qty_autos']
```

---

## Selecting Rows

### Filter rows by condition

```python
P.where("edad > 30")
```

Result:

| nombre | edad | qty_autos |
| ------ | ---- | --------- |
| Luis   | 40   | 2         |
| Pedro  | 36   | 0         |

Mathematical logic behind it:

$$
edad > 30
$$

---

### Extract specific rows

```python
P.datafil(1,3)
```

---

## Statistics

### Mean of all numeric columns

```python
P.mean()
```

Output:

```
(['edad','qty_autos'], [33.8, 1.2])
```

Mathematically:

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i
$$

---

### Mean of a specific column

```python
P.mean("edad")
```

Output:

```
33.8
```

---

### Count values

```python
P.count("nombre")
```

Output:

```
{'Ana': 1, 'Luis': 1, 'Pedro': 1, 'María': 1, 'Carla': 1}
```

---

### Unique values

```python
P.unique("nombre")
```

Output:

```
['Ana', 'Luis', 'Pedro', 'María', 'Carla']
```

---

### Most frequent values

```python
P.top("qty_autos")
```

Output:

```
qty_autos
1    2
2    2
0    1
Name: count, dtype: int64
```

---

## Index Management

### Set a column as index

```python
P.setindex("nombre")
```

### Reset index

```python
P.resetindex()
```

---

## Dataset Summary

```python
P.summary()
```

Example output:

```
rows: 5
fields: 3

nombre  text  unique: 5
edad    numeric  mean: 33.8
qty_autos numeric mean: 1.2
```

* Detects text columns (`text`) and numeric columns (`numeric`)
* Computes simple statistics (mean) for numeric columns

---

## Mathematical Interpretation

For numeric columns, statistics are computed using standard formulas:

**Mean:**

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i
$$

**Variance:**

$$
\sigma^2 = \frac{1}{n}\sum_{i=1}^{n} (x_i - \bar{x})^2
$$

**Standard deviation:**

$$
\sigma = \sqrt{\sigma^2}
$$

---

## Typical Workflow

```python
P.summary()
P.show()
P.mean("edad")
P.count("nombre")
P.where("edad > 30")
```

This allows students to **explore a dataset quickly**, understand numeric and text columns, and filter data easily.

---

## Notes for Beginners

* `qty` → quantity / number of rows
* `fields()` → list of columns
* `where()` → filter rows using logical conditions
* `mean()` → average of numeric columns
* `top()` → most frequent values
* `count()` → frequency of each unique value

All **pandas methods** are still available through `P`, e.g., `P.groupby("edad").sum()`.

---

**Philosophy:**

* Simplicity
* Readability
* Learning before complexity

Students first explore with **easy commands**, then can use full pandas features when ready.

```

---

Si quieres, maestro, puedo hacerte **la versión definitiva del script `lib_pandas.py` actualizado** con:

- `summary()` arreglado para Pandas ≥ 1.0  
- `mean()` que retorna valores numéricos  
- `where()` funcionando como alias de `selec()`  
- Todo listo para usar con CSV y mantener compatibilidad con pandas  

Así lo subes a GitHub y queda **profesional y educativo**.  

¿Quieres que haga eso?
```
