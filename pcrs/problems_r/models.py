from django.db import models
from django.core.exceptions import ValidationError
from problems.models import (AbstractProgrammingProblem,
							 SubmissionPreprocessorMixin,
							 AbstractSubmission,
							 AbstractTestCase,
							 AbstractTestRun,
							 testcase_delete, problem_delete)
from django.db.models.signals import post_delete
from pcrs.model_helpers import has_changed
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
	expected_output = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return "/problems/r/script/{}".format(self.pk)

	def get_base_url(self):
		return "/problems/r/script"

	def clean(self):
		r = RSpecifics()
		self.code = self.code.replace("\r", "")
		ret = r.run(self.code)
		if "exception" in ret:
			raise ValidationError(
				("R code is invalid. ")+ret["exception"])
		else:
			self.expected_output = ret["test_val"]
			self.save()
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

	def clean(self):
		self.solution = self.solution.replace("\r", "")

		if self.script:
			code = self.script.code+'\n'+self.solution
		else:
			code = self.solution

		r = RSpecifics()
		ret = r.run(code)

		if "exception" in ret:
			raise ValidationError(
				("R code is invalid. ")+ret["exception"])
		else:
			self.expected_output = ret["test_val"]
			self.max_score = 1
			self.save()

class Submission(SubmissionPreprocessorMixin, AbstractSubmission):
	"""
	Submission for an R problem
	"""
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	passed = models.BooleanField()

	def run_testcases(self, request):
		results = None
		error = None
		try:
			results = self.run_against_solution()
			if "exception" in results:
				error = results["exception"]
			return results, error
		except Exception:
			error = "Submission could not be run."
			return results, error

	def run_against_solution(self):
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

	def set_score(self):
		"""
		Score is 1 if passed, otherwise fail.
		"""
		ret = self.run_against_solution()
		if ret["passed_test"]:
			self.score = 1
		else:
			self.score = 0
		self.save()
		self.set_best_submission()

class TestCase(AbstractTestCase):
	"""
	R problem test case.
	"""
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE,
								null=False, blank=False)

class TestRun(AbstractTestRun):
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    def get_history(self):
        return {
            'visible': False,
            'input': '',
            'output': '',
            'passed': self.test_passed,
            'description': str(self.testcase)
        }

# update submission scores when a testcase is deleted
post_delete.connect(testcase_delete, sender=TestCase)

post_delete.connect(problem_delete, sender=Problem)