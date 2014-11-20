trim <- function(x) {
  gsub("(^[[:space:]]+|[[:space:]]+$)", "", x)
}

# Number of submissions for each question
number_submission <- function(filter, filter_field_num, matrix) {
  matrix = matrix[order(matrix[,1],matrix[,2], matrix[,3]),]
  
  # Remove studentID, problemID and time coluns
  remove_column_num = 3
  num_cols = ncol(matrix)-remove_column_num
  
  matrix_custom = matrix(data=0, nrow=0, ncol=num_cols)
 
  student_id = ""
  index = 0
  #print(paste("Number of negative submissions for question: ", filter))
  for(r in 1:nrow(matrix)){
    if(trim(matrix[r, filter_field_num]) == trim(filter)){
      if(student_id != matrix[r, 1]){
        matrix_custom <- rbind(matrix_custom, 0)
        index = index + 1
        student_id = matrix[r, 1]
      }
      for(c in 1:num_cols){
        if(matrix[r, (c+remove_column_num)] == 'f'){
          matrix_custom[index, c] = matrix_custom[index, c] + 1
        }
      }
    }
  }
  
  #print(matrix_custom)
  
  # Negative submission average for each question
  matrix_avg = matrix(data=1, nrow=1, ncol=num_cols)
  for(r in 1:nrow(matrix_custom)){
    for(c in 1:ncol(matrix_custom)){
      matrix_avg[1, c] = matrix_avg[1, c] + matrix_custom[r, c]
    }
  }
  #print("Number of tries:")
  #print(matrix_avg)
  #print("Number of tries average:")
  for(c in 1:ncol(matrix_avg)){
    #print(paste("Q",c,": ", matrix_avg[1, c] / nrow(matrix_custom)))
  }
  
}

# Create a new matrix for each graph (example: matrix for the first submission of exercise 3).
# This way we can plot a bar graph for each exercise and submission order
# We remove all columns just leaving the true/false ones
filter_matrix <- function(filter, filter_field_num, matrix, decreasing="", remove_column_num = 3) {
  if(decreasing != ""){
    # Order matrix to get first, or last submission
    if(decreasing == TRUE){
      matrix = matrix[order(matrix[,1],matrix[,2], matrix[,3]),]
    }else{
      matrix = matrix[order(matrix[,1],matrix[,2],-as.numeric((as.factor(matrix[,3])))), ]
    }
    unique = TRUE
  }else{
    unique = FALSE
  }
  # Remove studentID, problemID and time coluns
  num_cols = ncol(matrix)-remove_column_num
  # Create a 2 by 5 matrix to hold true/false values
  matrix_custom = matrix(data=0, nrow=2, ncol=num_cols)
  last_user = ""
  for(r in 1:nrow(matrix)){
    if(trim(matrix[r, filter_field_num]) == trim(filter)){
      if(unique == TRUE){
        if(matrix[r, 1] == last_user){
          next
        }
        last_user = matrix[r, 1]
      }
      for(c in 1:num_cols){
        if(matrix[r, (c+remove_column_num)] == 't'){
          matrix_custom[1, c] = matrix_custom[1, c] + 1
        }else{
          matrix_custom[2, c] = matrix_custom[2, c] + 1
        }
      }
    }
  }
  
  # Modify to percentage
  for(c in 1:ncol(matrix_custom)){
    total = as.numeric(matrix_custom[1, c]) + as.numeric(matrix_custom[2, c]);
    matrix_custom[1, c] = as.character(as.numeric(matrix_custom[1, c]) * 100 / total);
    matrix_custom[2, c] = as.character(as.numeric(matrix_custom[2, c]) * 100 / total);
    
  }
  return(matrix_custom)
}

# Create a new matrix to hold the number of attempts an student did 
# till he/she answered a problem set correctly
generate_attempts_matrix <- function(problem_set, input_matrix) {
  
  question_start = 4; 
  problem_col = 2;
  num_cols = 3;
  student_id = "";
  attempt_num = 1;
  index = 0;
  matrix_custom = matrix(data=0, nrow=0, ncol=num_cols)
  got_right = FALSE;
  
  for(r in 1:nrow(input_matrix)){
    if(trim(problem_set) == trim(input_matrix[r, problem_col])){
      if(student_id != input_matrix[r, 1]){
        matrix_custom <- rbind(matrix_custom, 0)
        index = index + 1;
        # Reset values
        student_id = input_matrix[r, 1];
        attempt_num = 1;
        got_right = FALSE;
      }
      if(input_matrix[r, question_start]   == 't' && 
         input_matrix[r, question_start+1] == 't' && 
         input_matrix[r, question_start+2] == 't' && 
         input_matrix[r, question_start+3] == 't' &&
         input_matrix[r, question_start+4] == 't'){
        got_right = TRUE;
      }else if(got_right == FALSE){
          attempt_num = attempt_num + 1;
      }
      matrix_custom[index, 1] = problem_set;
      matrix_custom[index, 2] = student_id;
      if(got_right == TRUE){
        matrix_custom[index, 3] = attempt_num;
      }else{
        matrix_custom[index, 3] = 999;
      }
    }
  }
  return (matrix_custom);
}


get_problem_label <- function(problem_id){
  problem_id = trim(problem_id);
  title = ""
  if(problem_id == "3"){
    title = "Warmup first section"
  }else if(problem_id == "28"){
    title = "Final test first section"
  }else if(problem_id == "30"){
    title = "Warmup second section"
  }else if(problem_id == "29"){
    title = "Final test second section"
  }else{
    title = paste("Problem Id: ", problem_id)
  }
  return (title);
}

# Global variable for using static file path
STATIC_PATH <- TRUE

# Choose file path interactively, or by using static path
if(STATIC_PATH == TRUE){
  mc_data_path = "/Users/danielmarchena/Desktop/workspace/PCRS/data_analysis/mc_data.csv"
  #code_data_path = "/Users/danielmarchena/Desktop/PCRS Analysis/code_data.csv"
}else{
  mc_data_path = file.choose(new = FALSE)
  #code_data_path = file.choose(new = FALSE)
}

# Read csv file - mc_data
mc_data = read.csv(mc_data_path, header=TRUE, sep=",")
mc_data <- as.matrix(mc_data) 

# Read csv file - code_data_path
#code_data = read.csv(code_data_path, header=TRUE, sep=",")
#code_data <- as.matrix(code_data) 

# Order mc_data by studentID, problemID and time attributes
mc_data = mc_data[order(mc_data[,1],mc_data[,2],mc_data[,3]), decreasing = TRUE]

# Create new mc_data matrix checking if student answer was right, or wrong
# We maintain the first 3 columns (studentId, problemID and time) and remove the extra columns (dividing by 2)
num_cols <- 3 + ((ncol(mc_data)-3)/2)
mc_data_mod = matrix(data=NA, nrow=nrow(mc_data), ncol=num_cols)

# List of unique exercise numbers in the CSV file
exercise_number_list = c()
for(r in 1:nrow(mc_data)){
  if((mc_data[r, 2] %in% exercise_number_list) == FALSE){
    exercise_number_list <- c(exercise_number_list,mc_data[r, 2])
  }
  index = 4 
  for(c in 1:num_cols){
    if(c > 3){
      if(mc_data[r, index+1] == 't'){
        mc_data_mod[r,c] = 't'
      }else{
        mc_data_mod[r,c] = 'f'
      }
      index = index+2
    }else{
      mc_data_mod[r,c] = mc_data[r, c]
    }
  }
}

for (exercise_id in exercise_number_list){
  attempts_matrix = generate_attempts_matrix(exercise_id, mc_data_mod);
  x_student_num = c()
  y_student_attempt = c()
  for(r in 1:nrow(attempts_matrix)){
    x_student_num <- cbind(x_student_num, strtoi(attempts_matrix[r, 2]))
    y_student_attempt <- cbind(y_student_attempt, strtoi(attempts_matrix[r, 3]))
  }
  h = hist(y_student_attempt, xlab="Number of attempts", main=get_problem_label(exercise_id), right=FALSE)
  h$density = h$counts/sum(h$counts)*100
  plot(h,freq=F, xlab="Number of attempts", ylab="Density %", main=paste(get_problem_label(exercise_id), "- %"))
  print(attempts_matrix);
}
# Warmup wilcox.test
wilcox_3 = generate_attempts_matrix("3", mc_data_mod)
y_wilcox_3 = c()
for(r in 1:nrow(wilcox_3)){
  y_wilcox_3 <- cbind(y_wilcox_3, strtoi(wilcox_3[r, 3]))
}

wilcox_30 = generate_attempts_matrix("30", mc_data_mod)
y_wilcox_30 = c()
for(r in 1:nrow(wilcox_30)){
  y_wilcox_30 <- cbind(y_wilcox_30, strtoi(wilcox_30[r, 3]))
}
print(wilcox.test(y_wilcox_3, y_wilcox_30, paired=FALSE))

# Final wilcox.test
wilcox_28 = generate_attempts_matrix("28", mc_data_mod)
y_wilcox_28 = c()
for(r in 1:nrow(wilcox_28)){
  y_wilcox_28 <- cbind(y_wilcox_28, strtoi(wilcox_28[r, 3]))
}

wilcox_29 = generate_attempts_matrix("29", mc_data_mod)
y_wilcox_29 = c()
for(r in 1:nrow(wilcox_29)){
  y_wilcox_29 <- cbind(y_wilcox_29, strtoi(wilcox_29[r, 3]))
}
print(wilcox.test(y_wilcox_28, y_wilcox_29, paired=FALSE))

# Order the list of unique exercises found in the CSV file
exercise_number_list = sort(exercise_number_list, )

# Create matrix with first right attempt

options_labels = c('True', 'False')
questions_labels = c('Q1','Q2','Q3','Q4','Q5')

# Divide the canvas to fit all graphs
par(mfrow=c(1,1))

for(exercise_num in exercise_number_list){
  # Filter by the problemID 
  filter = exercise_num 
  # The column position of problemID in the matrix is 2
  filter_field_num = 2
  number_submission(filter = filter, 
                    filter_field_num = filter_field_num, 
                    matrix = mc_data_mod)
                    
  mc_data_custom_first = filter_matrix(filter = filter, 
                                             decreasing = TRUE,
                                             filter_field_num = filter_field_num, 
                                             matrix = mc_data_mod)
  
  mc_data_custom_last = filter_matrix(filter = filter, 
                                            decreasing = FALSE,
                                            filter_field_num = filter_field_num, 
                                            matrix = mc_data_mod)
  
  
  # Labels sorted by first submission
  rownames(mc_data_custom_first) <- options_labels
  colnames(mc_data_custom_first) <- questions_labels
  
  # Labels sorted by last submission
  rownames(mc_data_custom_last) <- options_labels
  colnames(mc_data_custom_last) <- questions_labels
  
  title = get_problem_label(filter)
  
  par(mfrow=c(1, 1), mar=c(5,4,4,4))

  barplot(mc_data_custom_first, main=paste("First Sub - ", title), ylab="Percentage",
          xlab="Questions", legend.text = TRUE,
          args.legend = list(x = "topright", bty = "n", inset=c(-0.15, 0)))
          #args.legend = list(x = ncol(mc_data_custom_first)-4 , y=max(colSums(mc_data_custom_first))+10))
  #abline(h=mean(matrix(as.numeric(unlist(mc_data_custom_first)),nrow=nrow(mc_data_custom_first))))
  #means <- tapply(InsectSprays$count,InsectSprays$spray,mean)
  
  par(mfrow=c(1, 1), mar=c(5,4,4,4))
  #abline(h=mean(matrix(as.numeric(unlist(mc_data_custom_last)),nrow=nrow(mc_data_custom_last))))
  barplot(mc_data_custom_last, main=paste("Last Sub - ", title), ylab="Percentage",
          xlab="Questions", legend.text = TRUE,
          args.legend = list(x = "topright", bty = "n", inset=c(-0.15, 0)))
          #args.legend = list(x = ncol(mc_data_custom_last)-4 , y=max(colSums(mc_data_custom_last))+10))
  #m <- data.frame(matrix(as.numeric(unlist(mc_data_custom_last)),nrow=nrow(mc_data_custom_last)))
  #print(matrix(as.numeric(unlist(mc_data_custom_last)),nrow=nrow(mc_data_custom_last)))
  #abline(h=mean(matrix(as.numeric(unlist(mc_data_custom_last)),nrow=nrow(mc_data_custom_last))))
}