# DATA-WAREHOUSE
Data Manipulation System for SickZil-Machine

## Reusable Modules

### utils
Reusable (pure) functions **for any circumstance**. 

Fewer dependencies are better! If possible, DO NOT RELY ON ANY MODULES. \
DO NOT DEPEND project specific modules or codes. \
DO NOT DEPEND other utils modules. All utils modules can be used just as a single file.

### core
Reusable small and simple (pure) functions just **for this project**. \
core functions could not have side-effects...
Side-effects are discouraged. 

### tasks
Reusable more big functions across **Entity modules**. \
Tasks functions can read or write files or something... 
Side-effect are allowed, but generally discouraged.

## Entity Modules

### data
`Logics to add / generate data.` \
Data is raw data or relations(of data) from data source 
or external dataset. Some selected element(or atom) of data 
consists dataset.

If the relations of data is implicitly expressed through 
directory structure and file name, explicit data representation
(yaml, json) is not added to the data.

### dataset
`Logics to add / generate dataset.` \
Dataset is configured data things or relations from data.

### out
`Logics to generate trainable artifact` \
Out(put) is trainable representation of dataset.

## Interface
`cli.py` command line interface. Run `python main.py` to see
all commands. cli command calls funtions in entity modules. \
Some simple command can call tasks.functions directly.

`main.py` entry point. Call cli or tmp code for testing.
