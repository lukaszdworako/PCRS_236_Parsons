# fa_visuals app for PCRS



## Goals:
* Create automatable regex-to-DFA problems that accepts non-unique answers, and works around the subset inclusion algorithm.
* Use a visual front-end to assist in the intuition for students.

## Basic Usage:
* Instructor can add in regex (using relatively standardized notation), in a form similar to the short answer form.
* Student can use the visualizer on the submission page itself, and then get a text output.
* They can then input the text output into the submission text box and submit to get an answer.

## Guide:
### Instructor Side:
1. Log in, and click the `Problems` drop-down, and click `DFA Problems`
2. Click `+`.
3. The only differing input from short answer problems is the `regex` field. Use the given instructions to construct a regex, no need for slashes. It is assumed that all the characters in the regex are the alphabet.
4. Click `Save`. Problem can now be attempted.

### Student Side:
1. Go to the visualizer (the index.html that is currently in the visualixer folder).
2. Draw a DFA using the HTML canvas at the top of the page.
3. Click the button below to get the text output.
4. Put the text output into the text form.
5. Submit! If it is correct, then you will get a checkmark.

## Note to instructor:
* Regex conversion into DFA is not pre-processed, instead it is saved into the database with the first submission.
* All previous comments have been moved to README.old.md
* Tried to add the visualizer components to submission.html, but unfortunately CSRF came up.
* Couldn't finish all the tests, will finish that separately, but that's not being handed in for marks.

## Things that could be done that haven't been:
* Lack of feedback
* Lack of output to LaTeX/No saving on the canvas