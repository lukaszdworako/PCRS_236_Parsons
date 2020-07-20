### Completed: 

- Instructor side problem creation divded into two different pages. Required making a new model for Feedback, a new form, and new endpoints to update feedback and create it. Took a lot more time than I expected
- Added some functionality to the submissions. Student submissions are checked in the Submission model, and score sent back to the front end. This is not completely tested out yet -- as in, grading the solutions might be a bit flawed right not because I haven't completely tested it yet. Code requires a lot more error checking

- Instructor problems rendered with latex (use $ $ in proof). This actually took a lot lesser time than I expected, just had to source mathjax.


### To be completed: 

- Feedback. Problems are graded, but students can't see the feedback for incorrect answers yet, and hint buttons don't work yet. The reason for this is -- I want to look at existing PCRS problems, and see the way they render feedback on the front end side (with the green blanks) and follow the same model to be consistent. Same with hints -- I actually don't know if hints exist already so maybe i'll discuss a good way to render this with you. I could've looked at how feedback is rendered during this sprint -- but the main goal was dividing Problem creation up which took a lot more time than expected :') I think I'll be faster with rendering feedback because this doesn't really require going in and creating new models or even changing them. I just need to dig into the code and see the front end components being used. This is my priority now

- After finishing feedback reportiong and test cases for submissions I am hoping to make the instructor side more user friendly. I understand that asking instructors for JSON all the time is really annoying -- but I wanted to get the harder parts done first. This part should be fairly quick once I get Feedback and Test Cases done. 

### Example: 

1) Go to http://localhost:8000/problems/proof_blanks/list, and create a new problem with "+"
2) You can add "Prime Factorization" for the 'Name', "Prove that every natural number greater than 1 has a prime
factorization." for the proof statement, and an 'incomplete' proof:
<pre>
Predicate: P(n) : “There are primes p1, p2, . . . , pm (for some m $ge$
1) such that n = p1 p2 · · · pm.” We will show that ∀n $ge$ 2, P(n)

Base case:  n = {1}. Since {1} is prime, we can let p1 = {1} and say that
n = p1, so P({1}) holds.

Induction Hypothesis:  assume that for all {1}  $le$ i $le$ k, P(i) holds.  

Induction step:

There are two cases. In the first case, assume k + 1 is prime. Then
of course k + 1 can be written as a product of primes, so P(k + 1) is
true


In the second case, k + 1 is composite. But then by the definition of
compositeness, there exist a, b $\in$ N such that k + 1 = {2} and 2 $le$ a, b $\le$ k; that is, k + 1 has factors other than 1 and itself. This is the intuition from earlier. And here is the “recursive thinking”: by the induction
hypothesis, P(a) and P(b) hold. Therefore we can write 

a = q1 * ... * ql and b = r1 * ... * rl2
where each of the q’s and r’s is prime. But then

k + 1 = ab = q1 * ... * ql1 * r1 *...* rl2
and this is the prime factorization of k + 1. So P(k + 1) holds.
</pre>

3) `Answer Keys:` are `{"1": "2", "2": "a * b"}`, anything for `author and tags` and then `Save`

4) After you save, you should see the update problem page (i.e. the problem is saved) and see the `save and add feedback button`. Click this to add feedback

5) Add {"1": "{'type': 'int'}", "2": "{'mathexpr'}"} for `feedback` 

6) Can leave hints blank for now since I haven't added the functionaility yet so -- {} or just blank

7) You can either go back to the problem by clicking the link on the page and then press "Save and Attempt" or directly go to "{problem id}/submit" 

8) Try a variety of answers for the blanks -- but you will probably land up into an error unless you write 2 and a * b. This part needs testing, and I'm working on it now :)
