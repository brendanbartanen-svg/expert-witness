summarize_scores <- function(d) aggregate(score ~ treat, data = d, FUN = mean)
