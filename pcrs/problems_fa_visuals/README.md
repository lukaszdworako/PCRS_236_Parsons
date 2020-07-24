# Notes (Second Sprint):

## Completed:
* Created a template for student-side submission. It can validate very specific input, (I haven't tested anything too complicated, still working out), but it works for the string a* at the moment.

* Fixed a bunch of linking errors I had. Some of the existing html files didn't link to fa_visuals and instead linked to short_answers, running the wrong javascript.

* "Resolved" the dependency chain with PADS, by simply including the relevant file into the code(Originally I did resolve it, but then I found out about the code that needed to be edited). Not the best fix, but not only was there poor imports, there was Python2.7 code I had to alter to make into Python3, so I'll have to properly give credit to the authors in some manner. I don't really see a way around this, at the moment. Additionally, I couldn't really find a library that matched it in terms of functionality.

* Issues with PADS are documented in issues.md

## What remains:
* Adding fa_visuals to the navbar (small thing to do, but I should remember to do it)

* Fixing any kinks up with the DFA equality checker. I imagine this might take a bunch of time, considering how many issues PADS has given me in general, but since I've put the files locally, it shouldn't be too bad. Before I was trying to jump through hoops so as to not modify the source, but it seems that's more of an inevitability at this point.

* Adding visualization tool (if I have time) to fill out the app specifications laid out from the beginning.

* Addressing the fact that I'm a bunch of commits behind the current? I didn't really work on that.

* Documentation and general cleanup (removal of debug statements, etc).

## Example: 
* Go to http://localhost:8000/problems/fa_visuals/list, and create a new problem with "+"

* Use a* as your regex string.

* The answer should be: 
```a
1
1
1, a, 1
```

* Note: Please don't add an extra new line after, PCRS *might* crash. I'll work on that stuff for the next sprint.

# Notes (First Sprint):

* models.py cannot successfully import the PADS package (tried it for a couple hours to no avail)

# Questions:

1. What have you done so far?

A: I have created an app for the visualization, outlined a clear algorithm to use to test the user and have begun putting the algorithm in the app (have been met with quite a few difficulties). I have also modified the forms accordingly. You can view the forms at http://127.0.0.1:8000/problems/fa_visuals/list (replace localhost with whatever you're using).
~~The current commit does not run (at the time of writing), so I'll stash some of my changes and keep what I had finished.~

2. What I expected to get done.

A: I expected to have a very simple proof-of-concept that would have the form with the professor filling in a regular expression and then expecting (as very specific text input) a DFA from the student in a textbox and testing for correctness. The next goals would be then focused on properly putting the processing as pre-processing and then adding the visualization + interactive component to the student side.

3. Accomodations for difficulty you encountered.

A: The bulk of the Django/app development occured after June 22nd, where I had my last midterm. Since then I've had issues with:
- Django IMPORTED_APPS (I emailed you about this just earlier today)
- Django documentation (trying to use it to debug things and find fields that I can use is very difficult)
- PADS library (does. not. import.)
I'm not very proficient at checking long dependency chains and resolving very unhelpful errors, so it took me more than a couple days to fix these (the PADS error still going unfixed). I'm going to try to fix this in the next couple of days, but it's not going to be easy.

4. Where am I going to use this in 236/263?

A: As it stands, the project is currently taking in a regular expression input from the professor and (will) ask the student for a DFA input to test against the regular expression for correctness. Since this is supposed to use a user-friendly interface for the student, it will be very useful for the section about FSAs and regex.

