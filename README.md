```bash
python3 converter.py
usage: converter.py [-h] [--generate GENERATE] [-l LOG] [-y] [-r] PATH [PATH ...]
```

## Usage

Generic toc generation

By passing path to `tex` file and folder for output files generic structure will be generated

All actions means that `ThinkJava2` book is placed in `ThinkJava2` directory

Example: `python3 converter.py --generate ThinkJava2/thinkjava.tex example`

Generated config will be placed to `example` folder

### R markdown convert

[see subdocumentation](docs/bookdown.md)

## Config options

### workspace
* **directory** base directory of book
* **tex** book name
* **removeTrinket** remove trinket entries
* **removeExercise** remove exercise headers

Examples
```yaml
workspace:
  directory: ThinkJava2
  tex: thinkjava.tex
```

### assets

relative paths for assets, globing supports

Examples

```yaml
assets:
  - code
  - figs: "*.png"
```

### metadata

Global guides settings

Examples
```yaml
metadata:
  hideMenu: false
  protectLayout: false
```

Available options:

1. `scripts` - array of JS-script
1. `lexikonTopic` - string
1. `suppressPageNumbering` - `true|false` - Do not show section numbers
1. `useSubmitButtons` - `true|false` - Use Submit buttons
1. `useMarkAsComplete` - `true|false` - Show mark as complete
1. `hideMenu` - `true|false` - Hide top menu
1. `allowGuideClose` - `true|false` - Allow Guide to be closable
1. `collapsedOnStart` - `true|false` - Collapsed on start
1. `hideSectionsToggle` - `true|false` - Hide sections toggle
1. `hideBackToDashboard` - `true|false` - Hide "Back to dashboard" button
1. `protectLayout` - `true|false` - Prevent tabs closing by students


### sections

Pages rules

Examples
```yaml
sections:
  - name: Preface
    type: chapter
```

#### sections.configuration

The page configuration

Examples
```yaml
    configuration:
      layout: 2-panels
      files:
        - path: "code/ch03/GuessSoln.java"
          panel: 0
          action: open
```


Available options:
1. `layout` - string, guides layout, see Supported layouts
1. `learningObjectives` - string, learning objectives
1. `teacherOnly` - `true|false` - show only to teacher
1. `path` - array of string, open folder nodes in tree
1. `files` - array of file info objects, see File info objects

##### Supported layouts

1. `1-panel-tree` - 1 Panel with tree
1. `1-panel` - 1 Panel without tree
1. `2-panels-tree` - 2 Panels with tree
1. `2-panels` - 2 Panels without tree
1. `2-panels-guides-left` - 2 Panels without tree (Guides Left)
1. `3-columns-tree` - 3 Columns with tree
1. `3-columns` - 3 Columns without tree
1. `3-cell-tree` - 3 Panels with tree
1. `3-cell` -  Panels without tree
1. `3-cell-left` -  3 Panels without tree (Guides Left)
1. `4-cell-tree` -  4 Panels with tree
1. `4-cell` -  4 Panels without tree

##### File info objects
1. close all tabs (as first item in array)
```yaml
        - path: "#tabs"
          action: close
```
2\. open file, `panel` - panel number
```yaml
        - path: "code/ch03/GuessSoln.java"
          panel: 0
          action: open
```

3\. open preview, `panel` - panel number
```yaml
        - path: "#preview: https://codio.com/docs"
          panel: 0
          action: open
```

3\. execute terminal, `panel` - panel number
```yaml
        - path: "#terminal: echo \"hello\""
          panel: 0
          action: open
```

3\. python tutor visualizer, `panel` - panel number
```yaml
        - path: "#tutor: code/example.java"
          panel: 0
          action: open
```

3\. point code line in a file, `panel` - panel number, `ref` line content
```yaml
        - path: "test.html"
          panel: 0
          action: open
          ref: "line2"
          lineCount: 1
```

#### sections.transformations

transformation could be an string `skip` - remove item from procession or described below dicts

```yaml
    transformations: skip
```

The page transformations
Supports 2 transformations:

* add
```yaml
    transformations:
      - add: My simple text
        position: 79
      - add: |
          this is my very very very
          long string
          with multilines
        position: 244
```
* remove

```yaml
    transformations:
      - remove: 5
        position: 74
```

### Content not existed in book

It is possible to add own content via `insert_sections`

You should specify `chapter` and `section` which exists in book for identify a place for insert

```yaml
    chapter: Computer programming
    section: What is programming?
```

```yaml
insert_sections:
  - name: Exercises 1.1
    type: section
    chapter: Computer programming
    section: What is programming?
    before: false
    latex: |
      hello latex
  - name: Exercises 1.2
    type: section
    chapter: Computer programming
    section: What is programming?
    before: false
    markdown: |
      hello markdown
```


### Refs

Show available refs in book `python3 converter.py example -r`

You could override ref counting of `\ref` instruction by directive(changees in chapter counting)

```yaml
refs:
  chapter_counter_from: 0
```

Also you could override any `\ref` or `\pageref` output by `override rules`

```yaml
refs:
  overrides:
    JUnit:
      pageref: Testing with JUnit
      ref: '16.7'
    UML:
      pageref: 100
      ref: '11.7'
```

If you are using a `string` for `pageref` in generated md file prefix `in section` will be added
If a number - no additional

## Book generation

As we placed config to `example` directory, a book content could be generated by command

`python3 converter.py example`

Generated content will be placed to `example/generate` folder

## PDF to JPG

A book author used an PDFs as graphics in lot of places, so generation from pdf to jpg was added as markdown do not support PDFs preview

### First you need poppler-utils

pdftoppm and pdftocairo are the piece of software that do the actual magic. It is distributed as part of a greater package called [poppler](https://poppler.freedesktop.org/).

Windows users will have to install [poppler for Windows](http://blog.alivate.com.au/poppler-windows/), then add the `bin/` folder to [PATH](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/).

Mac users will have to install [poppler for Mac](http://macappstore.org/poppler/).

Linux users will have both tools pre-installed with Ubuntu 16.04+ and Archlinux. If it's not, run `sudo apt install poppler-utils`

Required a package `pip3 install pdf2image` 

## codestyle

[![wercker status](https://app.wercker.com/status/e4292419f5fdfef83fe74f7be72babb2/m/master "wercker status")](https://app.wercker.com/project/byKey/e4292419f5fdfef83fe74f7be72babb2)
