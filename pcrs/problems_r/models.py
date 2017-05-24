from django.db import models, DatabaseError
from django.core.exceptions import ValidationError
from problems.models import (AbstractProgrammingProblem,
							 SubmissionPreprocessorMixin,
							 AbstractSubmission,
							 AbstractTestCase,
							 AbstractTestRun,
							 testcase_delete, problem_delete,
							 FileUpload)
from django.db.models.signals import post_delete
from pcrs.model_helpers import has_changed
from pcrs.models import AbstractSelfAwareModel
from problems_r.r_language import *
from pcrs.settings import PROJECT_ROOT
from hashlib import sha1

import logging
import datetime
from django.utils.timezone import localtime, utc

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
	graphics = models.TextField(blank=True, null=True)

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
			self.graphics = ret["graphics"]
			# Handle the case where the new script already exists in the db
			try:
				self.save()
			except DatabaseError:
				logger = logging.getLogger('activity.logging')
				logger.error(str(localtime(datetime.datetime.utcnow().replace(tzinfo=utc))) + " | " +
					str(self.name) + " db entry exists")
				delete_graph(self.graphics)
				self.graphics = ""
		return ret

	def generate_graphics(self):
		r = RSpecifics()
		self.code = self.code.replace("\r", "")
		ret = r.run(self.code)
		if "exception" in ret:
			raise ValidationError(
				("R code is invalid. ")+ret["exception"])
		else:
			# Save new graphics path
			self.graphics = ret["graphics"]
			# Handle the case where the new script already exists in the db
			try:
				self.save()
			except DatabaseError:
				logger = logging.getLogger('activity.logging')
				logger.error(str(localtime(datetime.datetime.utcnow().replace(tzinfo=utc))) + " | " +
					str(self.name) + " db entry exists")
				delete_graph(self.graphics)
				self.graphics = ""
		return ret

class Problem(AbstractProgrammingProblem):
	"""
	An R problem is organized slightly differently
	from other languages like C, Python, Java, etc
	(it is more like an RDB problem in the way testing is done).
	Rather than having multiple testcases, a problem has:
		1.) a contextual pre-written Script, and
		2.) solution code
	Problems are checked by running the solution code which
	is appended after the Script (if one exists) and comparin outputs.
	"""
	language = models.CharField(max_length=50,
								choices=(("r", "R 3.3.2"),),
								default="r")
	script = models.ForeignKey(Script, null=True,
							   on_delete=models.CASCADE)
	sol_graphics = models.TextField(blank=True, null=True)
	output_visibility = models.BooleanField(default=True)

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
			# Delete generated graph
			if ret["graphics"]:
				delete_graph(ret["graphics"])
			self.max_score = 1
			self.save()

	def generate_sol_graphics(self, seed):
		# Checking whether there already is a graph in the cache
		if self.sol_graphics:
			path = os.path.join(PROJECT_ROOT, "languages/r/CACHE/", self.sol_graphics) + ".png"
			if os.path.isfile(path):
				return None

		self.solution = self.solution.replace("\r", "")

		code = "set.seed({})".format(seed)
		if self.script:
			code += '\n'+self.script.code+'\n'+self.solution
		else:
			code += '\n'+self.solution

		r = RSpecifics()
		code = code.replace("\r", "")
		ret = r.run(code)
		if "exception" in ret:
			raise ValidationError(
				("R code is invalid. ")+ret["exception"])
		else:
			# Save new graphics path
			self.sol_graphics = ret["graphics"]
			# Handle the case where the new script already exists in the db
			self.save()
		return ret

class Submission(SubmissionPreprocessorMixin, AbstractSubmission):
	"""
	Submission for an R problem
	"""
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	passed = models.BooleanField()
	data = models.ForeignKey(Filepload, on_delete=models.CASCADE)

	def run_testcases(self, request):
		print("RUNNING THE TESTS")
		results = None
		error = None
		try:
			results = self.run_against_solution()
			if "exception" in results:
				error = results["exception"]

			# Remove solution output if flag is false
			if not self.problem.output_visibility:
				results.pop("sol_graphics", None)
				results.pop("sol_val", None)

			return results, error
		except Exception:
			error = "Submission could not be run."
			return results, error

	def run_against_solution(self):
		"""
		Run the submission against the solution and return results.
		"""
		# Set common seed of solution and user based on hash of user id
		seed = self.get_seed()
		code = "set.seed({})".format(seed)
		sol_code = "set.seed({})".format(seed)

		# Preprocess tags in submission and append submission and solution to Script
		if self.problem.script:
			code = code+'\n'+self.problem.script.code+'\n'+\
				   self.preprocessTags()[0]['code']
			sol_code = sol_code+'\n'+self.problem.script.code+'\n'+\
					   self.problem.solution
		else:
			code = code+'\n'+self.preprocessTags()[0]['code']
			sol_code = sol_code+'\n'+self.problem.solution

		r = RSpecifics()
		ret = r.run_test(code, sol_code)
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

		# Delete generated graph
		if "graphics" in ret.keys() and ret["graphics"]:
			delete_graph(ret["graphics"])

		if "sol_graphics" in ret.keys() and ret["sol_graphics"]:
			delete_graph(ret["sol_graphics"])

		self.save()
		self.set_best_submission()

	def get_seed(self):
		"""
		Returns a seed based on the current user.
		"""
		hex_int = int(sha1(str.encode("{}".format(self.user))).hexdigest(), 16)
		user_int = hex_int + 0x200
		return user_int % 100000 # Make sure user_int is within R's int size limit

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

def delete_graph(graph):
	"""
	Deletes the given image from the CACHE of images.
	@param str graph
	"""
	if graph:
		path = os.path.join(PROJECT_ROOT, "languages/r/CACHE/", graph) + ".png"
		if os.path.isfile(path):
			os.remove(path)
