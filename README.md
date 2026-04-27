# 🚀 easypandas

> A simple and educational wrapper for pandas.

**easypandas** is designed to make data analysis easier to learn and use.
It simplifies the syntax of pandas while keeping its power under the hood.

---

## 🧠 Why easypandas?

[pandas](https://pandas.pydata.org/) is incredibly powerful, but:

* ❌ Syntax can be confusing for beginners
* ❌ Too many ways to do the same thing
* ❌ Hard to read for new learners

👉 **easypandas solves this by providing a clean, intuitive interface.**

---

## ✨ Philosophy

* ✅ Simple over complex
* ✅ Readable over cryptic
* ✅ Learning-focused design
* ✅ Keep the power of pandas

---

## ⚡ Quick Start

```python
from easypandas import easypandas

# Load data
P = easypandas("data.csv")

# Explore
P.show()
P.summary()

# Filter data
P.where("age > 30")

# Statistics
P.mean("salary")

# Fill missing values
P.fillna(0)

# Sort
P.sort("age", ascending=False)
```

---

## 🔥 Examples

### Filtering

```python
P.where("height > 180")
P.where("country == 'USA'")
P.where("age > 30 and salary < 5000")
```

---

### Selecting rows and columns

```python
P(0)                # row 0
P(0, 5)             # rows 0 to 5
P(0, 5, "name")     # rows 0-5, column "name"
P("A:D")            # column range
```

---

### Assign values (easy replacement for `.loc`)

```python
P.set([2,3], "Units Sold", 0)
P.assign([0,1], "age", 25)
```

---

### Handling missing values

```python
P.fillna(0)
P.fillna("Unknown", "city")
```

---

### Statistics

```python
P.mean("age")
P.min("salary")
P.max("salary")
P.freq("country")
```

---

### Combining datasets

```python
A = easypandas("file1.csv")
B = easypandas("file2.csv")

# Join
A.join(B, left="id", right="user_id", how="left")

# Append
A.append(B)
```

---

## 🧩 Design

easypandas uses a **wrapper pattern**:

* Internally uses pandas
* Externally exposes a simpler API
* Ensures consistent return types
* Supports method chaining

---

## 🎯 Target Users

* 📚 Students learning data analysis
* 👨‍🏫 Teachers explaining pandas concepts
* 🧪 Beginners exploring datasets
* ⚡ Anyone who wants simpler syntax

---

## 🚀 Installation

```bash
git clone https://github.com/aldotb/easypandas.git
cd easypandas
```

(You can later package it with pip)

---

## 🔮 Future Ideas

* `fillmean()` → fill with column mean
* `interpolate()` → smooth missing values
* `groupby_simple()` → beginner-friendly grouping
* Column autocomplete

---

## 🤝 Contributing

Contributions are welcome!

If you have ideas to make data analysis simpler, feel free to:

* open an issue
* submit a pull request

---

## 📜 License

MIT License

---

 

Built with ❤️ to make data analysis easier to learn.

If this project helps you, it truly **“vale un Perú”** 😄🔥
