## Project Proof Blanks



### Goals:

This project aims to provide students with fill-in-the-blank proofs that they can complete by using assisstance from hints and feedback when necessary. The motivation for doing this stems from the tendency of overlooking proof details, structure, and struggling with writing entire proofs when being introduced to new proofs. 



### Functionality: 

Other than the standard fill in the blanks usually done with string comparison, this project currently can grade solutions based on:

- **math expression equivalency (including instructor-student variable mapping)**: compares instructor math expression with student expression using sympy. If variables are defined in an ordered manner (only one new variable defined in a blank at a time), math expressions can be checked based on a variable-mapping so that both the instructor and student answers can have different variables.
- **instructor defined lambda boolean functions**: student answers can be checked using lambda functions given by instructors. If the lambda function returns "True" for the student answer, then the solution is correct else incorrect



### Usage Guide:

   #### Proof Creation:	

  1. Go to `/proof_blanks/create` to create a new proof (or alternatively click `+` on `/proof_blanks/list` )

  2. The `name`, `proof statement`, and `incomplete proof` are text inputs. They all support latex rendering with `$${latex here}$$` for non-inline latex code and `${latex here}$` for in-line latex. The **incomplete proof** also requires `{blank_id}` to be added anywhere you want to have a blank that should be filled with the correct answer to the blank. You can add as many of these blanks as necessary. For instance, in my example here all the `{1}` will be replaced by the student's correct answer to the blank. For example, if my incomplete proof is:
   ```
    Base case:  n = {1}. Since {1} is prime, we can let p1 = {1} and say that
    n = p1, so P({1}) holds.

```
And the student submits 2 as their answer to blank {1} (which happens to be correct) -- the incomplete proof displayed will be:
```
Base case:  n = 2. Since 2 is prime, we can let p1 = 2 and say that
n = p1, so P(2) holds.
```

  3. The `answer-keys` field is a JSON field and must follow the following structure:

     ```json
     {"blank_id": "default-answer", "1": "a * b", "2": "base case"}
     ```

     Each blank_id here should be unique. The corresponding value for the blank_id is the default answer that will be checked (using string comparison) in case there is a lack of feedback. 

     Notes: 

     - The maximum score for the problem will depend on the number of `blanks_ids`you have. Deleting any answer-keys will trigger re-evaluating all the submissions, and regrading them. 
     - Any math expressions provided as default answers will be evaluated as math expressions if `'type': 'mathexpr'` is added to feedback as defined below. The actual math expression needs to be added as the default answer here though. 
     - Math expressions can have variables but the operators **must be** python operators. (Check: https://www.tutorialspoint.com/python/python_basic_operators.htm)

		4. After you save this problem, an `Edit Feedback` button will be available at the bottom of the Problem form. You can click this to add feedback for submissions

		5. In the `feedback keys` JSON field, you can add feedback which follows the following structure:

     ```json
     {"blank_id": "{'this is the student answer string': 'this will be feedback for this string'}",
      "blank_id2": "{'type': 'mathexpr', 'map-variables': 'True'}", 
      "blank_id3": "{'type': 'int', 'lambda function of the form: lambda .+ : .+ (>|<|!|=)=? .+'}: 'correct'",
      }
     ```

     Setting the feedback to an answer to 'correct' will add to the student's score for the question.

     Notes: 

     - Defining the type is not needed for string comparisons, but is needed for math expressions and integers for conversion purposes
     - By default `map-variables` is set to False -- so you don't need to add it to the JSON if you don't want mapping
     - For now this only supports lambda functions matching the regular expression above. An example is: `lambda ans : ans >= 2`. If a lambda function is not provided for integer type, by default integer equivalence will be used to check the answer. 
     - "int" here is the python int

		6. In the `hint keys` JSON field, you can add hints which follow the following structure:

     ```json
     {"blank_id": "hint"}
     ```

     For now this project only supports one hint per problem, and hints are not based on student submissions. By default the student is not given any hints. 
     
     
     
  ### Proof Submission: (student side)
  - The incomplete proof is displayed to the student with text boxes to fill for blanks. Each blank has an associated hint button that the student can press to get a hint (if any are provided)
  - The student can click submit, and all the corresponding blanks will be filled with any correct responses from the student. This will be counted as a submission and if the student's grade is greater than previous grades it will be recorded as their current grade (like other PCRS problems)










