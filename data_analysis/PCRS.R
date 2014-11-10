trim <- function(x) {
  gsub("(^[[:space:]]+|[[:space:]]+$)", "", x)
}

# Create a new matrix for each graph (example: matrix for the first submission of exercise 3).
# This way we can plot a bar graph for each exercise and submission order
# We remove all columns just leaving the true/false ones
generate_specific_matrix <- function(filter, filter_field_num, matrix, decreasing="", remove_column_num = 3) {
  if(decreasing != ""){
    # Order matrix to get first, or last submission
    if(decreasing == TRUE){
      matrix = matrix[order(matrix[,1],matrix[,2],matrix[,3]), decreasing = decreasing]
    }else{
      matrix = matrix[order(matrix[,1],matrix[,2],matrix[,3]), ]
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
  return(matrix_custom)
}

# Global variable for using static file path
STATIC_PATH <-  TRUE

# Choose file path interactively, or by using static path
if(STATIC_PATH == TRUE){
  mc_data_path = "/Users/danielmarchena/Desktop/PCRS Analysis/mc_data.csv"
  #code_data_path = "/Users/danielmarchena/Desktop/PCRS Analysis/code_data.csv"
}else{
  mc_data_path = file.choose(new = FALSE)
  code_data_path = file.choose(new = FALSE)
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
      if(mc_data[r, index] == mc_data[r, index+1]){
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

# Order the list of unique exercises found in the CSV file
exercise_number_list = sort(exercise_number_list, )

options_labels = c('True', 'False')
questions_labels = c('Q1','Q2','Q3','Q4','Q5')

# Divide the canvas to fit all graphs
par(mfrow=c(1,1))
print(exercise_number_list)
for(exercise_num in exercise_number_list){
  # Filter by the problemID 
  filter = exercise_num 
  # The column position of problemID in the matrix is 2
  filter_field_num = 2
  mc_data_custom_first = generate_specific_matrix(filter = filter, 
                                             decreasing = TRUE,
                                             filter_field_num = filter_field_num, 
                                             matrix = mc_data_mod)
  
  mc_data_custom_last = generate_specific_matrix(filter = filter, 
                                            decreasing = FALSE,
                                            filter_field_num = filter_field_num, 
                                            matrix = mc_data_mod)
  print(mc_data_mod[1:1, ])
  
  # Labels sorted by first submission
  rownames(mc_data_custom_first) <- options_labels
  colnames(mc_data_custom_first) <- questions_labels
  
  # Labels sorted by last submission
  rownames(mc_data_custom_last) <- options_labels
  colnames(mc_data_custom_last) <- questions_labels
  
  barplot(mc_data_custom_first, main=paste("First Sub - Problem Id: ", filter), ylab="Quantity",
          xlab="Questions", legend.text = TRUE,
          args.legend = list(x = ncol(mc_data_custom_first)-4 , y=max(colSums(mc_data_custom_first))+10))
  
  barplot(mc_data_custom_last, main=paste("Last Sub - Problem Id: ", filter), ylab="Quantity",
          xlab="Questions", legend.text = TRUE,
          args.legend = list(x = ncol(mc_data_custom_last)-4 , y=max(colSums(mc_data_custom_last))+10))
}