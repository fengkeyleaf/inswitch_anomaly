# fengkeyleaf.my_pandas

## my_dataframe

### get_row_size

Get the row size for the give DataFrame.

---

### add_header

Add a header to a csv if there isn't a one.

---

### get_feature_content

Get specific data with the given features, except for the label.

---

## Builder

Class being the intermedia data structure to the pandas.DataFrame.

### add_column_name

Add column name(s) into this builder.

---

### add_row_name

Add row name(s) into this builder.

---

### append_element

Append an element into this builder. It's required that the last row has at least one empty spot.

---

### add_row

Add en entire rwo into this builder. THe new row name is required.

---

### reset

Reset this builder, clear its data.

---

### to_csv

Save this builder into a csv file.

---

### to_dataframe

Convert this builder into a Dataframe.