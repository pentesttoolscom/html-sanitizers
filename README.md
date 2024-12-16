# Server side sanitizers
Research on fuzzing HTML sanitizers in popular programming languages. You can read the accompanying presention [here](https://docs.google.com/presentation/d/1QrGNP6-8VD9hPVxJo6EoDH1eS4PfHmR5NyFhCKzdPr8/edit#slide=id.g213dfcddbe2_0_14).

## Project Structure

The project is split in three parts:

1. Under `web/` you will find all the code to deploy docker images of the sanitizers you want to fuzz.
2. Under `fuzz/` you will find all the code used for fuzzing the sanitizers
3. Under `github/` you will find a script to search through Github for repositories that use a vulnerable code pattern.

## Build

Place your fuzz targets in a separate directory each under `web/docker/backends`. Each subfolder there will be used as
a separate docker image and reachable at `http://localhost/subdir-name` at runtime. Currently we use one subfolder per
language. Each different sanitizer will be reachable at a different route as `http://localhost/subdir-name/sanitizer-name`

## Fuzz

The `fuzz` directory contains a basic fuzzer that tries to inject control characters inside a given fuzz template. Each fuzz template
is a file containing two sections:

- `[template]` contains the the text where the control characters will be injected. Each `_FUZZ_` string inside the text will be replaced
with a control character
- `[canary]` defines the string that we expect to find if the injection is succesful

An example is given in `fuzz/templates/example.fuzz`:
```
[template]
<a href='_FUZZ_java_FUZZ_script_FUZZ_:alert()'>G</a>

[canary]
javascript:alert()
```


## Search

`github/search.py` is a poor-man's REPL for searching Github for code: you give it a search query, it returns repos that
match that query, sorted by the number of stars. For each repo, you get back: the name, the number of stars, and the exact
line that matched. The search works just like the web interface, so you can give it modifiers like `path:*.py language:Python`.
You can find a reference [here](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax#about-code-search-query-structure).
