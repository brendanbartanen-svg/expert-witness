* master.do: fixture entry point. census.py must never run it.
version 18
clear all
global root ".."
do "01_clean.do"
capture noisily run "$root/code/02_tables"
* do "commented_out.do" is a comment, not a call
erase "sentinel.txt"
