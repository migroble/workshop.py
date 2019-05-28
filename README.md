# Dependencies
These are not necessary if you are using the binary release.  
[Python 3.5+](https://www.python.org/) - It's a Python script, so this one is kinda obvious.  
[Pyperclip](https://pypi.org/project/pyperclip/) - Used to copy rules to the clipboard. If it isn't found, the program will execute normally but it won't copy the rules directly into the clipboard.  

# Why this and not others
While other scripting languages currently available and in-development focus on making scripting easier and cleaner, the focus of this pseudo-language is to give the user metaprogramming capabilities. This means that for small simple scripts, those other languages will be a better choice in terms of clarity and usability; in the case of larger scripts, especially those with similar patterns in the rules themselves, this language will provide you with tools for much greater abstraction and reduced repetition.  

I don't expect most people to use this language, I mostly made it as a "proof of concept" to see if its possible to make a transpiler-like program without tokenizing and parsing and to explore how far I can abuse Python. The answers to these questions are: Yes, but regex can only get you so far for custom keywords, so at least some tokenizing is required if you want those; and a lot.

# Usage
Let's say you want to compile a script called `script.py`, then you would just run:  
`workshop.exe script.py` or `python workshop.py script.py`

This will copy the rules into your clipboard and you just have to paste them in the menu.

### Multiple scripts
You can also compile multiple scripts (effectively combining all the rules) by simply listing all the files you want to compile:  
`workshop.exe script1.py script2.py script3.py`

To compile all scripts in a directory would run:  
`workshop.exe directory\*`

### Output file
You can output the ruleset to a file by using the `-o` (`--output-file`) flag followed by the filename.

# Syntax
This scripting language is just Python with a little bit of syntactic sugar and a few extra built-in functions and constants.

## Rules
Rules are created by using the keyword `rule` followed by the name of your rule between quotes:  
```python
rule "this rule is epic":
	set_event(ongoing_each_player(all, all))
	add_action(kill(event_player, null))
```

You can also have a variable be the name of your rule:
```python
rule_name = "now, this is epic"

rule rule_name:
	pass
```

`pass` is the Python way of saying "do nothing", this creates an empty rule with event type "Ongoing - Global".

### Action/value names
Every action and value is named in the same way as they are in-game except, by default, dashes and spaces are replaced with underscores; dots, commas and colons are removed and all letters are lowercase.

There are 2 exceptions to this rule:  
* `and`, `or` and `not`: These have an underscore in front of their name (i.e. `_and`) because those keywords are already defined in Python.
* Variable names (`A`-`Z`): These are all uppercase simply because I personally think it looks better.

## Special functions

### Global/player variables
Global variables are accessed by prefixing `global_` to the variable letter (uppercase) and player variables are attributes of the player.

There are 4 built-in functions that return an action that sets or modifies a variable:  
* `set(variable, value)`: Sets a variable to a value
* `set_at_index(variable, index, value)`: Sets a variable to a value at an index
* `modify(variable, operation, value)`: Modifies a variable with an operation with value as its second argument
* `modify_at_index(variable, index, operation, value)`: Modifies a variable at an index with an operation with value as its second argument

```python
rule "player variable example":
	set_event(ongoing_each_player(all, all))
	
	add_condition(
		global_A == 5
		event_player.B == 0,
	)
	
	add_action(
		set(event_player.A, 1),
		set(global_A, 1),
		set_at_index(event_player.B, 0, 1)
		set_at_index(global_B, 0, 1),
		
		modify(event_player.A, "add", 1),
		modify_at_index(global_B, 0, "multiply", 2)
	)
```
These are just shorthands, you can still use `global_variable(A)` and `player_variable(event_player, B)` to access global and player variables respectively.

### Overloaded operators
Comparison operators, mathematical functions and array getters are overloaded. This means they can be used in the same way as you would in normal Python:  
```python
rule "operator example":
	add_condition(5 * (global_A[0] + 10) >= 0)
```

### Rule functions
* `set_event(event)`: Sets the event type.
* `add_action(*actions)`: Appends an action or action list or tuple to the action list.
* `add_condition(*conditions)`: Appends a condition or condition list or tuple to the condition list.

Actions and conditions not explicitly added to their respective list will be ignored.

### Adding many actions/conditions
To avoid having to call add_action/add_condition on many actions/conditions, you can group them up and call the function once:  
```python
rule "all for one":
	add_action(
		create_hud_text(event_player, string("oof", null, null, null), null, null, top, 100, white, white, white, visible_to_and_string),
		set(event_player.A, last_text_id),
		wait(1, ignore_condition),
		destroy_hud_text(event_player.A),
	)
```

Note that the actions are comma separated. You could also use `add_action([ action1, action2, ... ])`, `add_action((action1, action2, ...))` or even mix all styles `add_action(action1, [ action2, action3, ... ], ( action4, action5, ... ), ...)`.

## Switch
This feature is slightly odd in that it changes some of the things you are allowed to do and has a slightly unintuitive syntax.
A switch is piece of code that will be turned into an action list. This action list contains all the actions to make an if/else statement in the Overwatch workshop (basically, a bunch of `skip if`s and a skip at the end).  

### Switch syntax & limitations
To declare a switch you just have to use the `switch` keyword followed by the identifier of that switch, this will be the name of the variable that contains the action list the switch generates.  
For each condition you want to check, use the keyword `case` followed by the condition to start the chain of `skip if`s generated.
Now here is the rule-breaking part: These blocks of code **must** only have actions in them, although function calls that return an action list are fine as well.  

And now, for the example everyone was waiting for - a script that generates the Fibonacci sequence:
```python
rule "fibonacci":
	n = 20
	
	switch fib:
		case global_A == 0:
			set_at_index(global_B, 1, 0)
			set_at_index(global_B, 1, 1)
			set(global_A, 2)
		case:
			set_at_index(global_B, global_A, global_B[global_A - 1] + global_B[global_A - 2])
			modify(global_A, "add", 1)
	
	add_condition(global_A < n)
	add_action(fib, wait(0.016, abort_when_false), loop)
```

## Misc
### Classes, functions and variables
Since this is Python, you are free to create classes, functions and variables in the same way you would in normal Python:  
```python
rule "function and variable example":
	def add(a, b):
		return a + b
	
	value = add(event_player.A, 10)
	
	add_condition(value > global_variable(A))
```

### Math
A lot of mathematical functions can be approximated with a formula, since all math operators are overloaded, you can implement these functions trivially. Here's how you would implement arctan:
```python
# credit to LazyLion for the idea
def arctan(x, precision = 50):
    y = x
    sub = True
    for i in range(3, 3 + 2 * precision, 2):
        y += x**i / (-i if sub else i)
        sub = not(sub)
    return y
```
Note that this function would work for normal numbers as well as workshop values.


### Alternative cases
Because I'm a big fan of having bad ideas, the language provides you with the ability to choose which casing style you prefer:
* snake_case: The default case - All lowercase with underscores replacing spaces.
* PascalCase: The first letter of every word is capitalized and there are no spaces.
* camelCase: Same as pascal case, but the first letter is lowercase.
* bIkInIbOtToMcAsE: Because someone joked about it and now it's real.

This decision is done on a per-file basis to allow for interoperability with other scripts. To select which one you want, the first line of your script must be:  
`#case ` followed by `snake`, `pascal`, `camel` or `bikini bottom`

Special functions will also change case accordingly.

### Very advanced stuff
Since Python is a functional language, functions are first class types, this means they can be created just like any other variable.
For example you could make a function that returns other functions or, since rules are functions, a function that creates rules (rule factory):
```
def factory(name, value):
	rule name:
		set_event(ongoing_each_player(all, all))
		
		add_action(set_global_variable(A, value))

factory("epic rule #1", 0)
factory("epic rule #2", 1)
```

This will create two rules, both with `Ongoing - Each player(ALL, ALL)` event type and a `Set Global Variable` instruction with A as the first parameter but 0 and 1 as the second parameter for rule #1 and #2 respectively. This particular example isn't very exciting, but this feature is extremely powerful.  
Note that unlike actions and conditions, rules are implicitly added to the ruleset without needing to be called, defining them is enough.

# List of all overloaded operators

### Comparison operators
Operator | Function
 --- | --- 
`a < b` | `compare(a, less_than, b)`
`a <= b` | `compare(a, less_or_equal, b)`
`a == b` | `compare(a, equal, b)`
`a != b` | `compare(a, not_equal, b)`
`a > b` | `compare(a, greater_than, b)`
`a >= b` | `compare(a, greater_or_equal, b)`

### Logic operators
Operator | Function
 --- | --- 
`a & b` | `_and(a, b)`
`~a` | `_not(a)`
`a \| b` | `_or(a, b)`
`a ^ b` | `_and(_not(_and(self, other)), _or(self, other))`

### Mathematical operators
Operator | Function
 --- | --- 
`abs(a)` | `absolute_value(a)`
`a + b` | `add(a, b)`
`a // b` | `round(divide(self, other), down)`
`a @ b` | `dot_product(a, b)`
`a % b` | `modulo(a, b)`
`a * b` | `multiply(a, b)`
`-a` | `multiply(a, number(-1))`
`+a` | `absolute_value(a)`
`a ** b` | `raise_to_power(a, b)`
`a - b` | `subtract(a, b)`
`a / b` | `divide(a, b)`

### Array operators
Operator | Function
 --- | --- 
`a in b` | `array_contains(b, a)`
`countOf(a, b)` | `count_of(array, value)`
`a[b]` | `value_in_array(a, b)`
`a[b:c]` | `array_slice(a, b, c)`
`a.index(b)` | `index_of_array_value(a, b)`
