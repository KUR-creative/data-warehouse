# DATA-WAREHOUSE
Data Manipulation System for SickZil-Machine

## Reusable Modules

### utils
Reusable (pure) functions **for any circumstance**.

### core
Reusable pure functions just **for this project**. \
core functions DO NOT HAVE side-effects!

### tasks
Reusable functions across **Entity modules** \
tasks functions can read or write files or something... 
Side-effect allowed.

## Entity Modules

### data
`Logics to add / generate data.` \
Data is raw data or relations(of data) from data source 
or external dataset. Some selected element(or atom) of data 
consists dataset.

### dataset
`Logics to add / generate dataset.` \
Dataset is configured data things or relations from data.

### out
`Logics to generate trainable artifact` \
Out(put) is trainable representation of dataset.

## Interface
`cli.py` command line interface. Run `python main.py` to see
all commands. cli command calls funtions in entity modules.

`main.py` entry point. Call cli or tmp code for testing.
