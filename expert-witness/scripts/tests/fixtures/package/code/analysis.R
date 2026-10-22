# analysis.R: fixture R script
source("helpers.R")
# source("old_helpers.R") is commented out and must not be listed
scores <- read.csv("../data/scores.csv")
print(summarize_scores(scores))
