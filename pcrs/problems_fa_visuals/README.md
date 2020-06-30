**Notes:**

* models.py cannot successfully import the PADS package (tried it for a couple hours to no avail)

**Questions:**

1. What have you done so far?

A: I have created an app for the visualization, outlined a clear algorithm to use to test the user and have begun putting the algorithm in the app. I have also modified the forms accordingly. The current commit does not run (at the time of writing), so I'll stash some of my changes and keep what I had finished.

2. What I expected to get done.

A: I expected to have a very simple proof-of-concept that would have the form with the professor filling in a regular expression and then expecting (as very specific text input) a DFA from the student in a textbox and testing for correctness. The next goals would be then focused on properly putting the processing as pre-processing and then adding the visualization + interactive component to the student side.

3. Accomodations for difficulty you encountered.

A: The bulk of the Django/app development occured after June 22nd, where I had my last midterm. Since then I've had issues with:
- Django IMPORTED_APPS
- Django documentation
- PADS library
I'm not very proficient at checking long dependency chains and resolving very unhelpful errors, so it took me more than a couple days to fix these (the PADS error still going unfixed). I'm going to try to fix this in the next couple of days, but it's not going to be easy.

4. Where am I going to use this in 236/263?

A: As it stands, the project is currently taking in a regular expression input from the professor and (will) ask the student for a DFA input to test against the regular expression for correctness. Since this is supposed to use a user-friendly interface for the student, it will be very useful for the section about FSAs and regex.

