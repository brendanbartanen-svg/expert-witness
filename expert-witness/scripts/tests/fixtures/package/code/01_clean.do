* 01_clean.do: fixture cleaning step
import delimited "../data/scores.csv", clear
keep if !missing(score)
