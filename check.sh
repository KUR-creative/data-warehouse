autoflake --remove-all-unused-imports -r --in-place --exclude ./dw/util/fp.py . 
mypy 
pyflakes .
