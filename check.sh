autoflake --remove-all-unused-imports -r --in-place --exclude ./utils/fp.py . 
mypy .
pyflakes .
