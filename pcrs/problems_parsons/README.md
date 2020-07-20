### Completed: 
- Overall project core is mostly completed, including following features:
  - backend line comparison
  - backend execution of code using python testcases
  - frontend UI for both Instructor and Student side
    - functional Parsons puzzles in student side, with no exposed methods to force the correct result
    - Parsons Preview in instructor side, this serves no purpose other then just to see what the student will see
  - basic other PCRS functionality, monitor submissions, submission history, edit view, etc.
### To be completed: 
- Handle special cases, such as interchangable lines (this is theoretically possible, but I need to do some more experimentation)
- cleanup parsons.js as it leaves some exposed information that should not be there
- transfer everything from resources to static, allowing it to be compressed and sent, assisting with previous point thanks to "security by obscurity" ;)
- Decide for line type submission, what kind of feedback should be given, if any, as currently the ability to report specific incorrect lines is present in backend, but in frontend is not implemented, as well as various other kinds of errors
- Improve code assembly in backend, as there may be some possibility for odd cases to mess up how code is assembled
- Add support for tabbed grouped lines, in theory it is present, but perhaps there's a better way to do it


### Examples: 

For the below, you can technically run with any evaluation type selection, however safe default should be "Evaluate using all methods"

Basic interchangable line example:
  Starter code:
    def functionName(parameter):
        i = 2
        x = 2
        return parameter*i*x
  testcase:
    input: functionName(2)
    output: 8

Basic grouped lines example:
  Starter code:
    def starter_code(a):
      a= a*3<br>return a
  testcase:
    input: starter_code(1)
    output: 3
    
 Multi-Line single solution example:
  Starter code:
    def functionName(x, y):
      lst = []<br>for i in range(y):
        y = y**y
      for i in range(x):
        lst.append(x**y)
      return lst
  
