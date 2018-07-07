# shape

a python nested structure verify tool

## Rationale

When processing large and deeply nested json data, structrual exceptions often occur if the data quality is not assured. E.g. A missing dict key, an extra dict key that should not have existed, some miss-spellings or getting string "1" instead of number 1. They are just syntax valid json data, so IDEs would not help.

Things happens when json strings come from another system (maybe crude) that out of control, or it's input with keyboard or some copy-paste by another coder for temporary use, or both json producers and consumers are just started to work together and not familiar with a protocol with complex structure...

It's worse if data contains very long string, so it's not easy to check and correct it by your eyes. Even with pretty print, you still tend to overlook something facing long-long strings.

## Just be Defensive

In some of the cases, we ask maintainers to fix. While in some else, we need to take data with "dirty" structure into consideration. Our program could be strong enough, e.g. refuse to do further work if structural incorections are spotted, raise exception with hints, or try to do some simple fix. That is to be defensive.

Generally speaking, we would want to do this as soon as possible. Spotting an error just when we get the data, is better than it's delayed to be a weird exception in our main logic.

## And Declarative

If the data really nest deeply, there would be many layers of "for loops", many breaks and continues. It's hard to read, not explicit enough, because code readers must imagine the data structure through imperitive instructions.

That's how "shape" helps us. We just describe the nesting structure of data -- we call it the "shape" of data, then we get a checker that verifies anything that you give it. An example:

```python
Subject = T(str) & E(['sport', 'maths', 'literature'])

Question = Mpp(
    T(str) & C(lambda x: x.startswith('q')),  # q for "question"
    Dct({
        'question': T(str),
        'options': Seq(T(str)),
        'answer': OpK(T(str))
    })
)

Quiz = Dct({
    'subject': Subject,
    'questions': Question
})
```

Just like define classes, we define some "shapes". Then they can be used like:

```python
r = Quiz.verify({
    "subject": "sport",
    "questions": {
        "q1": {
            "question": "Which one is correct team name in NBA?",
            "options": [
                "New York Bulls",
                "Los Angeles Kings",
                "Golden State Warriros",
                "Huston Rocket"
            ],
            "answer": "Huston Rocket"
        }
    }
})

print(bool(r))
# True

print(r)
# <shape good>

assert r
```

if any tiny glitch is there, it would be found:

```python
r = Quiz.verify({
    "subject": "sport",
    "questions": {
        "q1": {
            "question": "Which one is correct team name in NBA?",
            "option": [
                "New York Bulls",
                "Los Angeles Kings",
                "Golden State Warriros",
                "Huston Rocket"
            ],
            "answer": "Huston Rocket"
        }
    }
})

print(bool(r))
# False

print(r)
# <shape bad: path: /questions/q1/options, error: not iterable>

assert r  # AssertionError
```

if you really throw some "trash" at it, it also refuse gentally:

```python
print(Quiz.verify(object()))
# <shape bad: path: /, error: not a dict>
```
 
## Common Checkers and Abbreviations

nearly all checkers can be found in the quiz example

### Structural Checkers

#### SequenceChecker (Seq)

a sequence checker accepts a sub-checker

pass if all elements in a sequence pass the sub-checker, otherwise fail

#### MappingChecker (Mpp)

a mapping checker accepts a key-checker and a value-checker

pass if all k-v pairs pass the key-chekcer and the value-chekcer, otherwise fail

#### DictChecker (Dct)

a dict checker accepts a dict, indicating the keys it should contain, and a sub-chekcer for each key

pass if all sub-checkers pass, otherwise fail

### Terminal Checkers

#### PredicateChecker (P) 

wrap an user-defined function as a predicate to be a checker

#### TypeChecker (T)

pass if it's instance of the type, otherwise fail

#### NoneChecker (N)

pass if None is given, otherwise fail

#### EnumChecker (E)

pass if something hit one of the enumeration, otherwise fail

### Logical Checkers

#### AndChecker (&)

pass if both checker-A and checker-B pass, otherwise fail

#### OrChecker (|)

pass if any of the checker-A and checker-B pass, otherwise fail

