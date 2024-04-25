library(tidyverse)
library(ggplot2)
library(lme4)
library(tidyverse)
library(data.table)
library(Hmisc)
library(dplyr)
library(readxl)
library(party)
library(randomForest)
library(randomForestExplainer)
library(caret)

###################
# 1. Load dataset #
###################
data <- read_excel("C:/Users/mycom/Desktop/D/Causative_alternation/data/data_20240410.xlsx")

data <- data %>% 
  mutate(Intentionality = ifelse(Intentionality == "Nint", "NInt", Intentionality)) %>% 
  mutate(across(c(Realization, Intentionality, Identifiabitlity, Spontaneity),
                as.factor)) 
set.seed(0329)
#################################
# 2. Conditional Inference Tree #
#################################
######################
# Visualization and EDA #
######################
model_CIT <- ctree(Realization ~ Intentionality + Identifiabitlity + Spontaneity, data = data,
                   controls = ctree_control(teststat = "quad",
                                            testtype = "Bonferroni",
                                            mincriterion = 0.95,
                                            minsplit = 20,
                                            minbucket = 7)) 

plot(model_CIT, main = "The result of Ctree", cex.main = 2) 
model_CIT

node_predictions <- predict(model_CIT, newdata = data, type = "node") 

data$Node <- as.factor(node_predictions) 

data %>% 
  select(Node, Realization) %>% 
  mutate(Realization = ifelse(Realization == "NCaus", 1, 0)) %>% 
  group_by(Node) %>% 
  summarise(NCaus_ratio = mean(Realization),
            Caus_ratio = 1-mean(Realization)) # Proportion of NCaus by Node
#########################
# Model evaluation #
#########################
trainIndex <- createDataPartition(data$Realization, p = .7, list = FALSE, times = 1) 
dataTrain <- data[trainIndex, ] 
dataTest <- data[-trainIndex, ] 

model_CIT <- ctree(Realization ~ Intentionality + Identifiabitlity + Spontaneity, data = dataTrain)

predictions_CIT <- predict(model_CIT, newdata = dataTest) 
accuracy_CIT <- sum(predictions_CIT == dataTest$Realization) / nrow(dataTest) 
cat("CIT Accuracy:", accuracy_CIT, "\n") 
table(predictions_CIT, dataTest$Realization) 

prob.CIT <- unlist(predict(model_CIT, newdata = dataTest, type = "prob")) 
prob.CIT_NCaus <- prob.CIT[seq(2, length(prob.CIT), by = 2)] 
somers2(prob.CIT_NCaus, ifelse(dataTest$Realization == "NCaus", 1, 0)) 

data_re <- read_excel("C:/Users/mycom/Desktop/D/Causative_alternation)/data/data_20240216.xlsx")

data_re <- data_re %>% 
  mutate(Intentionality = ifelse(Intentionality == "Nint", "NInt", Intentionality)) %>% 
  mutate(across(c(Realization, Intentionality, Identifiabitlity, Spontaneity),
                as.factor)) 

trainIndex_re <- createDataPartition(data_re$Realization, p = .7, list = FALSE, times = 1) 
dataTrain_re <- data_re[trainIndex_re, ] 
dataTest_re <- data_re[-trainIndex_re, ] 

model_CIT_re <- ctree(Realization ~ Intentionality + Identifiabitlity + Spontaneity, data = dataTrain_re)

predictions_CIT_re <- predict(model_CIT_re, newdata = dataTest_re) 
accuracy_CIT_re <- sum(predictions_CIT_re == dataTest_re$Realization) / nrow(dataTest_re) 
cat("CIT Accuracy:", accuracy_CIT_re, "\n")
table(predictions_CIT_re, dataTest_re$Realization) 

prob.CIT_re <- unlist(predict(model_CIT_re, newdata = dataTest_re, type = "prob"))
prob.CIT_NCaus_re <- prob.CIT_re[seq(2, length(prob.CIT_re), by = 2)] 
somers2(prob.CIT_NCaus_re, ifelse(dataTest_re$Realization == "NCaus", 1, 0))


################################
# 3. Conditional Random Forest #
################################
######################
# Visualization and EDA #
######################
model_CRF <- cforest(Realization ~ Intentionality + Identifiabitlity + Spontaneity, 
                     data = data, 
                     controls = cforest_control(mtry = 5, ntree = 500, replace = TRUE)) 

CRF.varimp <- varimp(model_CRF, conditional = TRUE) 
CRF.varimp

dotchart(sort(CRF.varimp), xlab = "Conditional Variable Importance", 
         main = "Conditional Variable Importance", 
         cex.axis = 1.2,  
         cex.main = 1.2,    
         cex = 1.2)       
abline(v = abs(min(CRF.varimp)), lty = 2, lwd = 2, col = "red") 

#########################
# Evaluation #
#########################
oob_predictions_CRF <- predict(model_CRF, OOB = TRUE, type = "response") 
oob_accuracy_CRF <- sum(oob_predictions_CRF == data$Realization) / nrow(data)
cat("CRF OOB Accuracy:", oob_accuracy_CRF, "\n") 
table(oob_predictions_CRF, data$Realization) 

prob.CRF <- unlist(predict(model_CRF, type = "prob")) 
prob.CRF_NCaus <- prob.CRF[seq(2, length(prob.CRF), by = 2)] 
somers2(prob.CRF_NCaus, ifelse(data$Realization == "NCaus", 1, 0)) 

########################################
# 4. Random forest #
########################################
model_RF <- randomForest(Realization ~ Intentionality + Identifiabitlity + Spontaneity, data = data,
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

###################################################
##########5. Mixed-effects logistic regression###########
###################################################
data=read.csv("C:/Users/user/OneDrive/Desktop/clean_data.csv")

head(data)

data = data %>% 
  mutate(across(c(Realization_NCaus,Intentionality_NInt,Spontaneity_Sp,Identifiabitlity_NIC), as.factor))

full_model <- glmer(Realization_NCaus ~ Intentionality_NInt+Spontaneity_Sp+Identifiabitlity_NIC
             +Intentionality_NInt*Spontaneity_Sp+Intentionality_NInt*Identifiabitlity_NIC+Spontaneity_Sp*Identifiabitlity_NIC
             +(1| verb), data= data,
             family = binomial, control = glmerControl(optimizer = "bobyqa"))

summary(full_model) 


fit2 <- glmer(Realization_NCaus ~ Intentionality_NInt+Identifiabitlity_NIC
             +(Spontaneity_Sp*Identifiabitlity_NIC)
             +(1| verb), data= data,
             family = binomial, control = glmerControl(optimizer = "bobyqa"))

summary(fit2) 
exp(fixef(fit2))


fix_estimate=fixef(fit2) 

fix_std= sqrt(diag(vcov(fit2))) 

upper = exp(fix_estimate+1.96*fix_std) #exp(beta)

lower = exp(fix_estimate-1.96*fix_std) #exp(beta)

exp_fix_estimate = exp(fix_estimate) #exp(beta)


fixed_interval=data.frame(upper= upper, lower=lower, coef = exp_fix_estimate, Term=names(fix_estimate))

########################
#Visualization of fixed effects #
########################
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
ggsave("C:/Users/user/OneDrive/Desktop/fixed_effect(close_ver).png", plot = p, width = 10, height = 8, dpi = 300)

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
ggsave("C:/Users/user/OneDrive/Desktop/fixed_effect(Full_ver).png", plot = p, width = 10, height = 8, dpi = 300)

fixed_interval
##########################
#Visualization of random effects #
##########################

random_effects <- ranef(fit2, condVar = TRUE)

random_effects_variances <- attr(random_effects[[1]], "postVar")


ran_var=vector() 

for (i in 1:135){
  ran_var[i]=random_effects_variances[[i]]
}
random_effects_sd <- sqrt(ran_var) 

upper = exp(random_effects$verb+1.96*random_effects_sd)

lower = exp(random_effects$verb-1.96*random_effects_sd)

ran_estimate = exp(random_effects$verb)

random_interval=data.frame(upper= upper[[1]], lower=lower[[1]], coef = ran_estimate[[1]], Term=rownames(ran_estimate))


write.csv(random_interval, 'C:/Users/user/OneDrive/Desktop/random_interval.csv')
selected_interval <- random_interval[random_interval$Term %in% c('break', 'fill', 'open', 'close', 'advance', 'improve', 'change', 
                                                                 'increase', 'explode', 'grow'), ]

selected_interval <- random_interval[random_interval$Term %in% c('break', 'fill', 'open', 'close', 'advance', 'improve', 'change', 
                                                                 'increase', 'explode', 'grow'), ]

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


ggsave("C:/Users/user/OneDrive/Desktop/Random_effect(main).png", plot = p, width = 10, height = 8, dpi = 300)


selected_interval <- random_interval[!random_interval$Term %in% c('break', 'fill', 'open', 'close', 'advance', 'improve', 'change', 
                                                                  'increase', 'explode', 'grow'), ]

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
  ggsave(paste0("C:/Users/user/OneDrive/Desktop/Random_effect", i, ".png"), plot = p, width = 10, height = 8, dpi = 300)
}

########
#C-index #
########
prob.cit <- predict(fit2, type = "response") 

actual_numeric <- as.numeric(data$Realization) - 1 
length(actual_numeric)
length(prob.cit)
c_index_result <- somers2(prob.cit, actual_numeric) 

print(c_index_result) 
