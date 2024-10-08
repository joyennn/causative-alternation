###################
# 0. Package Load #
###################
library(tidyverse)
library(readxl)
library(party)
library(randomForest)
library(Hmisc)
library(randomForestExplainer)
library(caret)
###################
# 1. Load dataset #
###################
data <- read_excel("C:/Users/mycom/Desktop/D/data_revised.xlsx")

data <- data %>% 
  select(-c(verb, sentence)) %>% 
  mutate(across(c(Realization, Intentionality, C.Identifiability, ExtCausality),
                as.factor)) 
set.seed(0909)
#################################
# 2. Conditional Inference Tree #
#################################
######################
# Visualization EDA#
######################
model_CIT <- ctree(Realization ~ Intentionality + C.Identifiability + ExtCausality, data = data,
                   controls = ctree_control(teststat = "quad",
                                           testtype = "Bonferroni",
                                           mincriterion = 0.95,
                                           minsplit = 20,
                                           minbucket = 7)) # Set CIT Model

plot(model_CIT, main = "The result of Ctree", cex.main = 2) 
model_CIT 

node_predictions <- predict(model_CIT, newdata = data, type = "node") # Get terminal node number

data$Node <- as.factor(node_predictions) # Attach the node number to original data for comparision

data %>% 
  select(Node, Realization) %>% 
  group_by(Node) %>% 
  summarise(NCaus_ratio = mean(as.numeric(Realization) - 1),
            Caus_ratio = 2-mean(as.numeric(Realization))) # Proportion of NCaus by Node

#########################
# Model evaluation #
#########################
# Splitting data
trainIndex <- createDataPartition(data$Realization, p = .7, list = FALSE, times = 1) 
dataTrain <- data[trainIndex, ] # Train Set (70%)
dataTest <- data[-trainIndex, ] # Test Set (30%)

model_CIT <- ctree(Realization ~ Intentionality + C.Identifiability
                  + ExtCausality, data = dataTrain)

predictions_CIT <- predict(model_CIT, newdata = dataTest) 
accuracy_CIT <- sum(predictions_CIT == dataTest$Realization) / nrow(dataTest) 
cat("CIT Accuracy:", accuracy_CIT, "\n") 
table(predictions_CIT, dataTest$Realization) 

# C-index 
prob.CIT <- unlist(predict(model_CIT, newdata = dataTest, type = "prob")) 
prob.CIT_NCaus <- prob.CIT[seq(2, length(prob.CIT), by = 2)] 
somers2(prob.CIT_NCaus, as.numeric(dataTest$Realization) - 1) 

################################
# 3. Conditional Random Forest #
################################
######################
# Visualization and EDA #
######################
model_CRF <- cforest(Realization ~ Intentionality + C.Identifiability + 
                       ExtCausality, data = data, 
                     controls = cforest_control(mtry = 2, ntree = 500, replace = TRUE)) 

CRF.varimp <- varimp(model_CRF, conditional = TRUE)
CRF.varimp 

dotchart(sort(CRF.varimp), xlab = "Conditional Variable Importance", 
         main = "Conditional Variable Importance", 
         cex.axis = 1.2,  
         cex.main = 1.2,    
         cex = 1.2)       
abline(v = abs(min(CRF.varimp)), lty = 2, lwd = 2, col = "red") 

oob_predictions_CRF <- predict(model_CRF, OOB = TRUE, type = "response") 
oob_accuracy_CRF <- sum(oob_predictions_CRF == data$Realization) / nrow(data) 
cat("CRF OOB Accuracy:", oob_accuracy_CRF, "\n") 
table(oob_predictions_CRF, data$Realization) 

# C-index 
prob.CRF <- unlist(predict(model_CRF, newdata = dataTest, type = "prob")) 
prob.CRF_NCaus <- prob.CRF[seq(2, length(prob.CRF), by = 2)] 
somers2(prob.CRF_NCaus, as.numeric(dataTest$Realization) - 1) 
########################################
# 4. RF & Interaction #
########################################
model_RF <- randomForest(Realization ~ Intentionality + C.Identifiability + 
                           ExtCausality, data = data,
                         oob.score = TRUE, localImp = TRUE) 

importance(model_RF) 
varImpPlot(model_RF, type=2, main="Variable Importance",
           cex.axis = 1.2,  
           cex.main = 1.2,    
           cex = 1.2) 

oob_predictions_RF <- predict(model_RF, OOB = TRUE, type = "response") 
oob_accuracy_RF <- sum(oob_predictions_RF == data$Realization) / nrow(data) 
cat("RF OOB Accuracy:", oob_accuracy_RF, "\n") 
table(oob_predictions_RF, data$Realization) 

min_depth_frame <- min_depth_distribution(model_RF) 
plot_min_depth_distribution(min_depth_frame) +
  theme(text = element_text(size = 16), 
        axis.title = element_text(size = 14), 
        axis.text = element_text(size = 16), 
        plot.title = element_text(size = 18), 
        legend.title = element_text(size = 12), 
        legend.text = element_text(size = 12)) 

importance_frame <- measure_importance(model_RF) 
vars <- important_variables(importance_frame, k = 3, measures = c("mean_min_depth", "no_of_trees")) 
interactions_frame <- suppressWarnings(min_depth_interactions(model_RF, vars)) 
plot_min_depth_interactions(interactions_frame) +
  theme(text = element_text(size = 13), 
        axis.title = element_text(size = 11), 
        axis.text = element_text(size = 11), 
        axis.text.x = element_text(angle = 60),
        plot.title = element_text(size = 18),
        legend.title = element_text(size = 10), 
        legend.text = element_text(size = 10)) 

data_2 = data %>% 
  mutate(across(c(Intentionality, C.Identifiability, ExtCausality),
                  as.numeric)) 

model_RF2 <- randomForest(Realization ~ Intentionality + C.Identifiability + 
                             + ExtCausality, data = data_2,
                          oob.score = TRUE, localImp = TRUE) 

plot_predict_interaction(model_RF2, data_2, "Intentionality", "C.Identifiability") +
  theme(text = element_text(size = 13), 
        axis.title = element_text(size = 11), 
        axis.text = element_text(size = 11), 
        plot.title = element_text(size = 16), 
        legend.title = element_text(size = 10), 
        legend.text = element_text(size = 10)) plot_predict_interaction(model_RF2, data_2, "Intentionality", "ExtCausality") +
  theme(text = element_text(size = 13), 
        axis.title = element_text(size = 11), 
        axis.text = element_text(size = 11), 
        plot.title = element_text(size = 16), 
        legend.title = element_text(size = 10), 
        legend.text = element_text(size = 10)) 
plot_predict_interaction(model_RF2, data_2, "C.Identifiability", "ExtCausality") +
  theme(text = element_text(size = 13), 
        axis.title = element_text(size = 11), 
        axis.text = element_text(size = 11), 
        plot.title = element_text(size = 16), 
        legend.title = element_text(size = 10), 
        legend.text = element_text(size = 10)) 

########################################
# 5. Mixed-effects logistic regression #
########################################
library(tidyverse)
library(ggplot2)
library(lme4)
library(tidyverse)
library(data.table)
library(Hmisc)
library(dplyr)
library(readxl)


data=read_excel("C:/Users/82105/Desktop/updated_data.xlsx") 

data = data %>% 
  mutate(across(c(Realization_Ncaus), as.factor))

full_model <- glmer(Realization_Ncaus ~ Intentionality_NIntent+C.Identifiability_RC+ExtCausality_IntCOS
                    +Intentionality_NIntent*C.Identifiability_RC*ExtCausality_IntCOS
                    +(1| verb), data= data,
                    family = binomial, control = glmerControl(optimizer = "bobyqa"))

summary(full_model) 

fit2 <- glmer(Realization_Ncaus ~ Intentionality_NIntent+C.Identifiability_RC+ExtCausality_IntCOS
              +(1| verb), data= data,
              family = binomial, control = glmerControl(optimizer = "bobyqa"))

summary(fit2) 


exp(fixef(fit2))


fix_estimate=fixef(fit2) 

fix_std= sqrt(diag(vcov(fit2))) 

upper = exp(fix_estimate+1.96*fix_std) 

lower = exp(fix_estimate-1.96*fix_std) 

exp_fix_estimate = exp(fix_estimate) #exp(beta)

fixed_interval=data.frame(upper= upper, lower=lower, coef = exp_fix_estimate, Term=names(fix_estimate))
fixed_interval

###################################################
#############6. Visualization of fix effects #################
###################################################
#fixed effects close ver.
p=ggplot(fixed_interval, aes(y=Term))+
  geom_point(aes(exp_fix_estimate))+
  geom_errorbarh(aes(xmin = fixed_interval$lower, xmax = fixed_interval$upper), height = 0.1)+
  geom_vline(xintercept = 1, linetype = "dashed", color = "gray")+
  xlim(0,10)+
  theme(axis.title.x = element_blank(), 
        axis.title.y = element_blank(), 
        axis.text.x = element_text(size=12), 
        axis.text.y = element_text(size=12), 
        plot.title = element_text(hjust = 0.5, size=16)
  ) +
  labs(title = 'Fixed effects')

p
ggsave("C:/Users/82105/Desktop/fixed_effect(close_ver)_수정.png", plot = p, width = 10, height = 8, dpi = 300)

#fixed effects full ver.
p=ggplot(fixed_interval, aes(y=Term))+
  geom_point(aes(exp_fix_estimate))+
  geom_errorbarh(aes(xmin = fixed_interval$lower, xmax = fixed_interval$upper), height = 0.1)+
  geom_vline(xintercept = 1, linetype = "dashed", color = "gray")+
  theme(
    axis.title.x = element_blank(), 
    axis.title.y = element_blank(), 
    axis.text.x = element_text(size=12), 
    axis.text.y = element_text(size=12), 
    plot.title = element_text(hjust = 0.5, size=16) 
  ) +
  labs(title = 'Fixed effects')
p
ggsave("C:/Users/82105/Desktop/fixed_effect(Full_ver)_수정.png", plot = p, width = 10, height = 8, dpi = 300)

fixed_interval
###################################################
############7. Visualization of random effects ###############
###################################################
random_effects <- ranef(fit2, condVar = TRUE)#random effect estimae and Variance

random_effects_variances <- attr(random_effects[[1]], "postVar")#Random effects variance


ran_var=vector() 

for (i in 1:135){
  ran_var[i]=random_effects_variances[[i]]
}
random_effects_sd <- sqrt(ran_var) 

upper = exp(random_effects$verb+1.96*random_effects_sd) 

lower = exp(random_effects$verb-1.96*random_effects_sd) 

ran_estimate = exp(random_effects$verb) 

#random effects 95% confidence interval
random_interval=data.frame(upper= upper[[1]], lower=lower[[1]], coef = ran_estimate[[1]], Term=rownames(ran_estimate))

write.csv(random_interval, 'C:/Users/82105/Desktop/random_interval_수정.csv')
selected_interval <- random_interval[random_interval$Term %in% c('close', 'fill', 'open', 'advance', 'diminish', 'improve', 'explode', 'grow', 'increase'), ]

selected_interval <- random_interval[random_interval$Term %in% c('close', 'fill', 'open', 'advance', 'diminish', 'improve', 'explode', 'grow', 'increase'), ]

p=ggplot(selected_interval, aes(y=Term))+
  geom_point(aes(coef))+
  geom_errorbarh(aes(xmin =lower, xmax = upper), height = 0.1)+
  geom_vline(xintercept = 1, linetype = "dashed", color = "gray")+
  theme(
    axis.title.x = element_blank(), 
    axis.title.y = element_blank(), 
    axis.text.x = element_text(size=12), 
    axis.text.y = element_text(size=12), 
    plot.title = element_text(hjust = 0.5, size=16) 
  ) +
  labs(title = 'Random effects')


ggsave("C:/Users/82105/Desktop/Random_effect(main)_수정.png", plot = p, width = 10, height = 8, dpi = 300)

selected_interval <- random_interval[!random_interval$Term %in% c('close', 'fill', 'open', 'advance', 'diminish', 'improve', 'explode', 'grow', 'increase'), ]
for (i in 1:13) {
  if (10 * i < length(selected_interval$Term)) {
    p <- ggplot(selected_interval[(10 * (i - 1) + 1):(10 * i), ], aes(y = Term, x = coef)) +
      geom_point() +
      geom_errorbarh(aes(xmin = lower, xmax = upper), height = 0.1) +
      geom_vline(xintercept = 1, linetype = "dashed", color = "gray") +
      theme(
        axis.title.x = element_blank(), 
        axis.title.y = element_blank(), 
        axis.text.x = element_text(size=12), 
        axis.text.y = element_text(size=12), 
        plot.title = element_text(hjust = 0.5, size=16) 
      ) +
      labs(title = 'Random effects')
  } else {
    p <- ggplot(selected_interval[(10 * (i - 1) + 1):length(selected_interval$Term), ], aes(y = Term, x = coef)) +
      geom_point() +
      geom_errorbarh(aes(xmin = lower, xmax = upper), height = 0.1) +
      geom_vline(xintercept = 1, linetype = "dashed", color = "gray") +
      theme(
        axis.title.x = element_blank(), 
        axis.title.y = element_blank(), 
        axis.text.x = element_text(size=12), 
        axis.text.y = element_text(size=12), 
        plot.title = element_text(hjust = 0.5, size=16) 
      ) +
      labs(title = 'Random effects')
  }
  
  print(p)
  ggsave(paste0("C:/Users/82105/Desktop/Random_effect_수정", i, ".png"), plot = p, width = 10, height = 8, dpi = 300)
}

###################################################
################8. C-index ####################
###################################################
prob.cit <- predict(fit2, type = "response") 

actual_numeric <- as.numeric(data$Realization_Ncaus) - 1 
length(actual_numeric)
length(prob.cit)
prob.cit
c_index_result <- somers2(prob.cit, actual_numeric) 

print(c_index_result) 

png("C:/Users/82105/Desktop/qqnorm_plot.png", width = 800, height = 600, res = 150)

qqnorm(resid(fit2))
qqline(resid(fit2), col = "red") 

dev.off()
