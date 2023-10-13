# P4-16 Types and Operations Supported in Tofino

## 1. Introduction

Since the Intel® Tofino™ Native Architecture (TNA) is a P4-16 architecture that provides a P4 programming interface[^1] and we don't have the documentation for it right now, **I will use the one[^2] for P4-16 provided by P4.org for reference**. I will update this documentation once I get the documentation for Tofino. 

## 2. Supported Types

P4 supports the following built-in base types:

- `bool`, which represents Boolean values
- `int`, which represents arbitrary-sized constant integer values
- Bit-strings of fixed width, denoted by `bit<>`
- Fixed-width signed integers represented using two's complement `int<>`
- Bit-strings of dynamically-computed width with a fixed maximum width `varbit<>`

### 2.1 bool

The Boolean type `bool` contains just two values, `false` and `true`. Boolean values are not integers or bit-strings.

### 2.2 int (Infinite-precision integers)

This type is reserved for integer literals and expressions that involve only literals. For example:

```c
const int a = 5;
const int b = 2 * a;
const int c = b - a + 3;
```

### 2.3 Unsigned integers (bit-strings)

An unsigned integer (which we also call a “bit-string”) has an arbitrary width, expressed in bits. A bit-string of width `W` is declared as: `bit<W>`. For example:

```c
const bit<32> x = 10;   // 32-bit constant with value 10.
const bit<(x + 2)> y = 15;  // 12-bit constant with value 15.
                            // expression for width must use ()
```

### 2.4 Signed Integers (Fixed-width signed integers)

Bits within an integer are numbered from `0` to `W-1`. Bit `0` is the least significant, and bit `W-1` is the sign bit.

For example, the type `int<64>` describes the type of integers represented using exactly 64 bits with bits numbered from 0 to 63, where bit 63 is the most significant (sign) bit.

### 2.5  Dynamically-sized bit-strings

The type varbit<W\> denotes a bit-string with a width of at most W bits, where W must be a non-negative integer that is a compile-time known value. For example, the type varbit<120> denotes the type of bit-string values that may have between 0 and 120 bits. Most operations that are applicable to fixed-size bit-strings (unsigned numbers) cannot be performed on dynamically sized bit-strings.

## 3. Supported Operations

### 3.1 bool

The following operations are provided on Boolean expressions: - “And”, denoted by `&&` - “Or”, denoted by `||` - Negation, denoted by `!` - Equality and inequality tests, denoted by `==` and `!=` respectively.

The precedence of these operators is similar to C and uses short-circuited evaluation where relevant.

### 3.2 int (Infinite-precision integers)

The type `int` supports the following operations:

- Negation, denoted by unary `-`
- Unary plus, denoted by `+`. This operation behaves like a no-op.
- Addition, denoted by `+`.
- Subtraction, denoted by `-`.
- Comparison for equality and inequality, denoted by `==` and `!=` respectively. These operations produce a Boolean result.
- Numeric comparisons `<,<=,>`, and `>=`. These operations produce a Boolean result.
- Multiplication, denoted by `*`.
- Truncating integer division between positive values, denoted by `/`.
- Modulo between positive values, denoted by `%`.
- Arithmetic shift left and right denoted by `<<` and `>>`. These operations produce an `int` result. The right operand must be either an unsigned constant of type `bit<S>` or a non-negative integer compile-time known value.

### 3.3 Unsigned integers (bit-strings)

The type `bit<>` supports the following operations:

- Test for equality between bit-strings of the same width, designated by `==`. The result is a Boolean value.
- Test for inequality between bit-strings of the same width, designated by `!=`. The result is a Boolean value.
- Unsigned comparisons `<,>,<=,>=`. Both operands must have the same width and the result is a Boolean value.
- Negation, denoted by unary `-`. The result is computed by subtracting the value from 2W. The result is unsigned and has the same width as the input. The semantics is the same as the C negation of unsigned numbers.
- Unary plus, denoted by `+`. This operation behaves like a no-op.
- Addition, denoted by `+`. This operation is associative. The result is computed by truncating the result of the addition to the width of the output (similar to C).
- Subtraction, denoted by `-`. The result is unsigned, and has the same type as the operands. It is computed by adding the negation of the second operand (similar to C).
- Multiplication, denoted by `*`. The result has the same width as the operands and is computed by truncating the result to the output's width. P4 architectures may impose additional restrictions — e.g., they may only allow multiplication by a non-negative integer power of two.
- Bitwise “and” between two bit-strings of the same width, denoted by `&`.
- Bitwise “or” between two bit-strings of the same width, denoted by `|`.
- Bitwise “complement” of a single bit-string, denoted by `~`.
- Bitwise “xor” of two bit-strings of the same width, denoted by `^`.
- Saturating addition, denoted by `|+|`.
- Saturating subtraction, denoted by `|-|`.

### 3.4 Signed Integers (Fixed-width signed integers)

The type `int<>` supports the following operations:

- Negation, denoted by unary `-`.
- Unary plus, denoted by `+`. This operation behaves like a no-op.
- Addition, denoted by `+`.
- Subtraction, denoted by `-`.
- Comparison for equality and inequality, denoted `==` and `!=` respectively. These operations produce a Boolean result.
- Numeric comparisons, denoted by `<,<=,>,` and `>=`. These operations produce a Boolean result.
- Multiplication, denoted by `*`. Result has the same width as the operands. P4 architectures may impose additional restrictions—e.g., they may only allow multiplication by a power of two.
- Bitwise “and” between two bit-strings of the same width, denoted by `&`.
- Bitwise “or” between two bit-strings of the same width, denoted by `|`.
- Bitwise “complement” of a single bit-string, denoted by `~`.
- Bitwise “xor” of two bit-strings of the same width, denoted by `^`.
- Saturating addition, denoted by `|+|`.
- Saturating subtraction, denoted by `|-|`.

### 3.5 Dynamically-sized bit-strings

Variable-length bit-strings support a limited set of operations:

- Assignment to another variable-sized bit-string. The target of the assignment must have the same static width as the source. When executed, the assignment sets the dynamic width of the target to the dynamic width of the source.
- Comparison for equality or inequality with another `varbit` field. Two `varbit` fields can be compared only if they have the same type. Two varbits are equal if they have the same dynamic width and all the bits up to the dynamic width are the same.

### 3.6 Summary

| Types                         | Addition | Subtraction | Multiplication | Division                                                   |
| ----------------------------- | -------- | ----------- | -------------- | ---------------------------------------------------------- |
| Infinite-precision integers   | Y        | Y           | Y              | Y(Truncating integer division between **positive** values) |
| Unsigned integers             | Y        | Y           | Y              |                                                            |
| Fixed-width signed integers   | Y        | Y           | Y              |                                                            |
| Dynamically-sized bit-strings |          |             |                |                                                            |

According to the comparison table above, only infinite-precision integers in P4-16 supports division, and no floating point numbers are supported.

---

[^1]:[P416 Intel® Tofino™ Native Architecture – Public Version](https://github.com/barefootnetworks/Open-Tofino/blob/master/PUBLIC_Tofino-Native-Arch.pdf)
[^2]: [P4-16 Version 1.2.3](https://staging.p4.org/p4-spec/docs/P4-16-v-1.2.3.html?_ga=2.157999612.772950233.1697048558-1363716787.1693766125&_gl=1*1iaj65q*_ga*MTM2MzcxNjc4Ny4xNjkzNzY2MTI1*_ga_VXXZD2250K*MTY5NzA1ODQ1Mi45LjEuMTY5NzA1ODkwMC4wLjAuMA..*_ga_FW0Q4274RH*MTY5NzA1ODQ1MS45LjEuMTY5NzA1ODkwMC4wLjAuMA..)
