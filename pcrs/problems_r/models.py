from django.db import models
from django.core.exceptions import ValidationError
from problems.models import (AbstractProgrammingProblem,
							 SubmissionPreprocessorMixin,
							 AbstractSubmission)
from pcrs.models import AbstractSelfAwareModel
from problems_r.r_language import *

class Script(AbstractSelfAwareModel):
	"""
	Prepared R code that serves as context for R problems.
	If an R problem has a Script, submissions will be appended
	to the Script and then executed.

	Must be valid R script.
	"""
	name = models.SlugField(max_length=30, unique=True)
	code = models.TextField(blank=False, null=False)

	def __str__(self):
		return self.name

	def run_script(self):
		"""
		Run Script
		"""
		r = RSpecifics()
		ret = r.run(self.code)
		if "exception" in ret:
			raise ValidationError({"exception": ret["exception"]})
		
		return ret

class Problem(AbstractProgrammingProblem):
	"""
	An R problem is organized slightly differently
	from other languages like C, Python, Java, etc 
	(it is more like an RDB problem in the way testing is done). 
	Rather than having multiple testcases, a problem has:
		1.) a contextual pre-written Script, and
		2.) solution code
	Its expected_output is updated by executing
	the solution code, which is appended after the Script (if one exists).
	"""
	language = models.CharField(max_length=50,
								choices=(("r", "R 3.3.2"),),
								default="r")
	script = models.ForeignKey(Script, null=True, 
							   on_delete=models.CASCADE)
	expected_output = models.TextField(blank=True, null=True)

	def update_expected_output(self):
		"""
		Run R problem solution with its Script
		and update its expected_output field.
		"""
		if self.script:
			code = self.script.code+'\n'+self.solution
		else:
			code = self.solution

		r = RSpecifics()
		ret = r.run(code)
		if "exception" in ret:
			raise ValidationError({"exception": ret["exception"]})
		else:
			self.expected_output = ret["test_val"]

class Submission(SubmissionPreprocessorMixin, AbstractSubmission):
	"""
	Submission for an R problem
	"""
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

	def run_against_solution(self, request):
		"""
		Run the submission against the solution and return results.
		"""
		# Preprocess tags in submission and append to Script
		if self.problem.script:
			code = self.problem.script.code+'\n'+\
				   self.preprocessTags()[0]['code']
		else:
			code = self.preprocessTags()[0]['code']

		r = RSpecifics()
		ret = r.run_test(code, self.problem.expected_output)
		return ret