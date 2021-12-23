<!-----
NEW: Check the "Suppress top comment" option to remove this info from the output.

Conversion time: 0.67 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β31
* Thu Dec 23 2021 12:14:23 GMT-0800 (PST)
* Source doc: B* DOCS
----->


_B*: DOCUMENTATION_

_(With 0% less bot! Coming soon™)_

**_First Edition, prerelease copy._**

**_By BowlingPizzaBall#2470, Inferno#3671, LegitSi#4444, weee50#8913, and Zelo101#0138_**

**_=== BASIC EXPLANATION ===_**

This is a successor to new B++. Unlike the transition from oldtag to newtag, newtag to b*tag is much easier, as all of your code is already backwards compatible. This means that you can just paste in your old programs and they'll work fine. If you aren’t already familiar, tags are miniature programs, such as those made in B++ or B*, and generally ran through a Discord bot.

**_=== TERMS ~~AND CONDITIONS~~ ===_**

Some terms in this might not be clear.  \
b*tag = b* tags. Usually used to differentiate from other versions. Third & latest version of tags..

Oldtag = the first form of tags.

Newtag = the second form of tags.

**_=== ALL FUNCTIONS ===_**

The B* programming language is composed of functions. These functions have a variety of uses from defining to choosing to labeling. Here, every single function in the language is listed.

Short List (Current functions [some in progress] ):` DEFINE, VAR, MATH, COMPARE, IF, ARRAY, CHOOSE, CHOOSECHAR, REPEAT, CONCAT, RANDINT, RANDOM, FLOOR, CEIL, ROUND, INDEX, ABS, ARGS, GLOBAL DEFINE, GLOBAL VAR, MOD `


```
-> DEFINE :: Defines a variable name v as an arbitrary value that can be called again later with the name s
	Format: [DEFINE s v]
	-> s: must be a string composed only of letters, numbers or underscores, and cannot start with a number
	-> v: can be pretty much anything
	Returns an empty string, meaning this function by itself does not affect the program output

-> VAR :: Calls for the value of a variable name s that's already defined
	Format: [VAR s]
	-> s: must be a variable name that has already been defined
	Returns the value the variable was last set with

-> MATH :: Allows addition (+), subtraction (-), multiplication (*), division (/), and exponentiation (^) between two numbers n1 and n2
	Format: [MATH n1 op n2]
	-> n1: has to be a number
	-> op: has to be a string of either + - * / or ^
	-> n2: has to be a number
	Further restrictions apply depending on the operation
	Returns a number (integer if applicable, float otherwise)
[Math should be depreciated [12/14/21, inferno], since it's replaced by the new functions]

-> COMPARE :: Compares two values v1 and v2 with comparisons of larger-than (>), smaller-than (<), larger-or-equal-to (>=), smaller-or-equal-to (<=), equal-to (=), and not-equal-to (!=)
	Format: [COMPARE v1 op v2]
	-> v1: can be pretty much anything
	-> op: has to be a string of either > < >= <= = or !=
	-> v2: has to be the same type as v1
	Returns an integer of either 0 (comparison is false) or 1 (comparison is true)

-> IF :: Returns one of two values v1 or v2 depending on the result of a comparison c
	Format: [IF c v1 v2]
	-> c: can be pretty much anything, but usually an integer. Values equivalent to 0 are false, everything else translates to true
	-> v1: can be pretty much anything
	-> v2: can be pretty much anything
	Returns v1 if c is true and v2 if c is false

-> ARRAY :: Defines an array containing all the elements provided in the input list
	Format: [ARRAY i1 i2 i3...]
	-> i: can be pretty much anything
	Returns an array

-> CHOOSE :: Randomly chooses an element of either an array or an input list with equal chance for each one
	Format: [CHOOSE i1 i2 i3...] or [CHOOSE a]
	-> i: can be pretty much anything
	-> a: has to be an array, elements can be pretty much anything
	Returns one of the values provided

-> CHOOSECHAR :: Randomly chooses a single character of a string s provided
	Format: [CHOOSECHAR s]
	-> s: has to be a string
	Returns a string of one character

-> REPEAT :: Repeats a string or array v a given number n of times
	Format: [REPEAT v n]
	-> v: has to be either a string or array
	-> n: has to be an integer
	Returns either a string or an array, depending on input v

-> CONCAT :: Concatenates an arbitrary number of strings, numbers or arrays together
	Format: [CONCAT i1 i2 i3...]
	-> i: strings or non-nested arrays*, with numbers parsed as strings
	Returns a string.
    * Nested arrays do work but may not work as you expect. This is mainly due to how it is programmed. We plan to fully support it in the future, so I wouldn't use nested array CONCATing for now.
	Modified 12/14/21 by Inferno, we support arrays & strings now 

-> RANDINT :: Returns a random integer between the lower number  INCLUSIVE and the higher number EXCLUSIVE. The lower and higher numbers can take any order in n1 and n2
	Format: [RANDINT n1 n2]
	-> n1: has to be an integer
	-> n2: has to be an integer
	Returns an integer

-> RANDOM :: Returns a random float between the lower and higher numbers. The lower and higher numbers can take any order in n1 and n2
	Format: [RANDOM n1 n2]
	-> n1: has to be a number
	-> n2: has to be a number
	Returns a float

-> FLOOR :: Rounds a number n down
	Format: [FLOOR n]
	-> n: has to be a number
	Returns an integer

-> CEIL :: Rounds a number n up
	Format: [CEIL n]
	-> n: has to be a number
	Returns an integer

-> ROUND :: Rounds a number n to the nearest integer. As per IEEE 754 default standard, .5 is rounded to the closest even integer.
	Format: [ROUND n]
	-> n: has to be a number
	Returns an integer

-> INDEX :: Takes the element n of a string or array v. Indices count from 0.
	Format: [INDEX v n]
	-> v: can be a string or an array
	-> n: has to be an integer
	Returns pretty much anything if v is an array, or a single character string if v is a string

-> ABS :: Takes the absolute value of a real number n.
	Format: [ABS n]
	-> n: has to be a number
	Returns a number (integer if applicable, float otherwise)

-> ARGS :: Returns the value of the nth message argument included in the tag command. Arguments can only be provided when using a saved program (tc/b++ [program]), and are counted as being any text separated by spaces after the program name. Counting starts from 0.
	Format: [ARGS n] or [ARGS] (beta!)
	-> n: has to be an integer
	Returns a string corresponding to the argument. The string will be empty if no nth argument exists. If no n is provided, it will give an array of all arguments.

-> GLOBAL DEFINE :: Defines a global variable name v as an arbitrary value that can be called again later with the name s. Global variables can be used in any program. Only one global variable with name v can exist at a time. Whoever first creates a global variable becomes its owner, and from that point onward the variable can only be edited if it's done so in a program written by the variable owner.
	Format: [GLOBAL DEFINE s v]
	-> s: must be a string composed only of letters, numbers or underscores, cannot start with a number, must not correspond to a global variable the program author does not own
	-> v: can be pretty much anything
	Returns an empty string, meaning this function by itself does not affect the program output

-> GLOBAL VAR :: Calls for the value of a global variable name s that's already defined. Any program can call global variables.
	Format: [GLOBAL VAR s]
	-> s: must be a variable name that has already been defined
	Returns the value the global variable was last set with

-> # :: A comment function. Anything inside the tag will not show up in the output nor be processed by the program, leaving it as text that's only visible in the program code.
	Format: [# text]
	-> text: can be pretty much anything
	Returns an empty string, meaning this function by itself does not affect the program output

-> MOD :: Returns the number n1 modulo n2
	Format: [MOD n1 n2]
	-> n1: has to be a number
	-> n2: has to be a non-zero number
	Returns a number (int if applicable, float otherwise)
```


**_=== OTHER DOCUMENTS ===_**

Starter’s Guide:

Credits(?):
