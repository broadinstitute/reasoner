library(readr)
library(dplyr)
library(ggplot2)

cop_file <- './data/cop_benchmark.csv'
results_file <- './data/q2.results.summary.txt'

outfile <- './data/cop_overlap.csv'

cop <- read_csv(cop_file) %>% mutate(Drug = tolower(Drug), origin="truth", probability = 1)
results <- read_tsv(results_file) %>% mutate(origin="prediction", Tissue = '')

matches_cop <- cop %>% select(Drug, Target = PrimaryTargetLabel, Pathway = Pathway_Target_MeSH_Label, 
                          Cell = Anatomy_Cell_MeSH_Label, Tissue = Anatomy_Tissue_MeSH_Label, Symptom = Symptom_MeSH_Label,
                          Disease = ConditionName, probability, origin) %>% filter(Drug %in% results$Drug)

matches_results <- results %>% select(Drug, Target, Pathway, Cell, Tissue, Symptom,
                                      Disease, probability, origin) %>% filter(Drug %in% matches_cop$Drug)

matches <- rbind(matches_cop, matches_results) %>% arrange(Drug, desc(origin))

write.csv(matches, file = outfile)
