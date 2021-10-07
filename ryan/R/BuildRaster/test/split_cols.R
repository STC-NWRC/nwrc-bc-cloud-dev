library(dplyr)
library(tidyr)

before <- data.frame(
  attr = c(1, 30 ,4 ,6 ), 
  type = c('foo_and_bar', 'foo_and_bar_2')
)

before %>%
  separate(type, c("foo", "bar"), "_and_")