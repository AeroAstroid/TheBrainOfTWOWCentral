## B* starter guide
last updated 13/11/2021

B* is a programming language

## 0. Using the bot

To get the list of commands you can use, type `b/help`.

## 1. Hello world

Hello world is actually very simple, all you have to do is type:

```
Hello, World!
```

like B++, B* effectively echos any strings given to it!

## 2. B* Functions

Think of a function as a machine that takes an input, changes said input then outputs the manipulated input.
For example, the function `[REPEAT]` would repeat something a given amount of times.

Functions can be nested, to create more complex programs.
This is called functional programming.

Here is an example of nested functions:

```
[REPEAT [CONCAT "Hello, " "World!" " "] 10]
```

This would first concatenate the three strings `"Hello, "`, `"World!"` and `" "` to `"Hello, World! "`

_Notice how I've added a space to the end of the concatenated string. This is so that there will be a space between every repeated "Hello, World!"._

The string `"Hello, World! "` will then be repeated `10` times to give the output:

```
Hello, World! Hello, World! Hello, World! Hello, World! Hello, World! Hello, World! Hello, World! Hello, World! Hello, World! Hello, World!
```

_Also notice how the space at the end was cut off. B* automatically trims any spaces at the start or end of the output. This is only done at the end of the program, not during._

## 3. Types

The type of data you input to a function can change the way the function works. Let's talk about each one.

### String / Literal

Think of a string as an array of characters contained within quotes. Just like how a word is made out of multiple characters, a string is completely the same.

**Examples:**
```
"Hello, World!"
"1234567"
"[WHATS UP]"
```

### Integer

An Integer is a whole number, so no decimals.

**Examples:**
```
101
367863467575846375
-145252
```

### Float

A Float is a rational number.

**Examples:**
```
101.0
239548754298534.2352857254
-52181.12
1.50e40
```

### Array

An array is a list of data. The listed data does not need to be the same type, but it's recommended, to avoid complexity.

**Examples:**
```
[ARRAY 1 2 3 4 5]
[ARRAY "test" 9999 [REPEAT "hello" 5]]
```

### Functions

Functions are also types!
