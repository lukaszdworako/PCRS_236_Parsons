from django.db import models, DatabaseError
from django.core.exceptions import ValidationError
from django.utils.timezone import localtime, utc
from django.utils.encoding import smart_str
from problems.models import (AbstractProgrammingProblem,
							 SubmissionPreprocessorMixin,
							 AbstractSubmission,
							 AbstractTestCase,
							 AbstractTestRun,
							 testcase_delete,
							 problem_delete,
							 FileUpload)
from django.db.models.signals import post_delete
from pcrs.model_helpers import has_changed
from pcrs.models import AbstractSelfAwareModel
from problems_r.r_language import *
from pcrs.settings import SITE_PREFIX, PROJECT_ROOT, SECRET_KEY
from hashlib import sha1
from users.models import PCRSUser

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

import logging, datetime, time, shutil

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
		return "{}/problems/r/script/{}".format(SITE_PREFIX, self.pk)

	def get_base_url(self):
		return "{}/problems/r/script".format(SITE_PREFIX)

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
	data_set = models.ForeignKey(FileUpload, null=True, on_delete=models.CASCADE)
	sol_graphics = models.TextField(blank=True, null=True)
	output_visibility = models.BooleanField(default=True)
	allow_data_set = models.BooleanField(default=True)

	def clean(self):
		"""
		Checks validity of Problem and saves to db.

		@return None
		"""
		self.solution = self.solution.replace("\r", "")

		if self.script:
			code = self.script.code+'\n'+self.solution
		else:
			code = self.solution

		if self.data_set:
			inst_code = load_dataset(self.data_set.get_str_data())
			code += inst_code

		r = RSpecifics()
		ret = r.run(code)

		if "exception" in ret:
			raise ValidationError(
				("R code is invalid. ")+ret["exception"])
		else:
			# Delete generated graph
			if "graphics" in ret.keys() and ret["graphics"]:
				delete_graph(ret["graphics"])
			self.max_score = 1
			self.save()

	def generate_sol_graphics(self, seed):
		"""
		Generates the solution's graphics.

		@param int seed
		@return {}
		"""
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

	def generate_export_zip(self):
		"""
		Generates a zip of all best Submissions for each student for this Problem.
		"""
		# Create a temporary folder to be zipped
		path = os.path.join(PROJECT_ROOT, "languages/r/CACHE/EXPORT_{}".format(self.pk))
		if not os.path.exists(path):
			os.makedirs(path)

		# Query for the best submissions
		sbms = Submission.objects.filter(problem=self, has_best_score=True)
		for submission in sbms:
			submission.create_pdf(path)

		# Zip the folder
		zip_dest = os.path.join(PROJECT_ROOT, "languages/r/CACHE/Problem_{}".format(self.pk))
		shutil.make_archive(zip_dest, 'zip', path)
		zip_dest += '.zip' # Reuse variable adding .zip for full path

		# Delete the folder
		shutil.rmtree(path)

		# Return path to zipped folder
		if os.path.exists(zip_dest):
			return zip_dest
		else:
			return None

class Submission(SubmissionPreprocessorMixin, AbstractSubmission):
	"""
	Submission for an R problem
	"""
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	passed = models.BooleanField(default=True)

	def build_code(self, code, data_set):
		"""
		Builds string of code using Submission's fields.
		Builds code in the following order:
			1. Default user hash seed
			2. Script
			3. Instructor's data set
			4. Data set
			5. Submission/Solution code

		@param str code
		@return str
		"""
		return_code = ""

		# Set common seed of solution and user based on hash of user id
		seed = self.get_seed()
		return_code = "set.seed({})".format(seed)

		# Append Script if it exists
		if self.problem.script:
			return_code += '\n'+self.problem.script.code

		# Use instructor's data set if it exists
		if self.problem.data_set:
			inst_code = load_dataset(self.problem.data_set.get_str_data())
			return_code += '\n'+inst_code

		# Use submitted data set if it exists
		if data_set and self.problem.allow_data_set:
			data_code = load_dataset(data_set)
			return_code += '\n'+data_code

		# Append actual user code
		return_code += '\n'+code

		return return_code

	def run_testcases(self, request):
		"""
		Asseses students by comparing user output to solution output.

		@param HttpRequest request
		@return [{}, str]
		"""
		results = None
		error = None
		try:
			# Add file upload to submission
			data_set = self.get_dataset()

			results = self.run_against_solution(data_set)
			if "exception" in results:
				error = results["exception"]

			# Remove solution output if flag is false
			if not self.problem.output_visibility:
				delete_graph(results["sol_graphics"])
				results.pop("sol_graphics", None)
				results.pop("sol_val", None)

			return results, error
		except Exception:
			error = "Submission could not be run."
			return results, error

	def run_against_solution(self, data_set):
		"""
		Run the submission against the solution and return results.

		@param str data_set
		@return {}
		"""
		code = self.build_code(self.preprocessTags()[0]['code'], data_set)
		sol_code = self.build_code(self.problem.solution, data_set)

		if "system" in code or "eval" in code or "parse" in code:
			ret = {"passed_test": False, "exception": "Unsupported R command used"}
			return ret

		r = RSpecifics()
		ret = r.run_test(code, sol_code)
		return ret

	def set_score(self, request):
		"""
		Score is 1 if passed, otherwise fail.

		@param HttpRequest request
		@return None
		"""
		# Add file upload to submission
		data_set = self.get_dataset()

		ret = self.run_against_solution(data_set)
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

		@return int
		"""
		hex_int = int(sha1(str.encode("{}".format(self.user))).hexdigest(), 16)
		user_int = hex_int + 0x200
		return user_int % 100000 # Make sure user_int is within R's int size limit

	def header(self, canvas, doc):
		"""
		Draws a header on the current page of the canvas.

		@param canvas canvas
		@param SimpleDocTemplate doc
		@return None
		"""
		# Save state so we can draw on it
		canvas.saveState()
		styles = getSampleStyleSheet()

		# Setup header flowable
		date = datetime.datetime.now().strftime("%Y-%m-%d")
		hash_str = self.generate_stu_hash()
		header_text = "<font size=12>" + self.user.username + " | " + self.problem.name \
					  + " | " + date + " | " + hash_str + "</font>"
		header = Paragraph(header_text, styles["Normal"])
		w, h = header.wrap(doc.width, doc.topMargin)
		header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

		# Release the canvas
		canvas.restoreState()

	def create_pdf(self, dir_path=None):
		"""
		Creates a pdf from submission.

		@return str
		"""
		# Setting up ReportLab
		file_name = self.user.username + '_' + str(self.problem.pk) + '_' \
					+ str(self.pk) + '.pdf'
		if dir_path:
			pdf_path = os.path.join(dir_path, file_name)
		else:
			pdf_path = os.path.join(PROJECT_ROOT, "languages/r/CACHE/", file_name)
		doc = SimpleDocTemplate(pdf_path,pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=36,bottomMargin=18)
		styles=getSampleStyleSheet()


		# Building text elements of pdf
		Story=[]
		br_code = self.preprocessTags()[0]["code"].replace('\n','<br />\n')
		code = "<para><font size=12 name='Courier'>" + br_code + "</font></para>"

		# Generate user's output
		try:
			fsm = FileSubmissionManager.objects.get(user=self.user, problem=self.problem)
			preprocessed_data = fsm.file_upload.get_str_data()
			data_set = load_dataset(preprocessed_data)
		except:
			data_set = None
		user_code = self.build_code(self.preprocessTags()[0]['code'], data_set)
		r = RSpecifics()
		user_code = user_code.replace("\r", "")
		ret = r.run(user_code)
		if "exception" in ret:
			raise ValidationError(
				("R code is invalid. ")+ret["exception"])

		if ret["test_val"]:
			output = "<para><font size=12 name='Courier'>" \
					+ ret["test_val"].replace('\n','<br />\n') + "</font></para>"
		else:
			output = None

		Story.append(Paragraph("<font size=18>Code</font>", styles["Normal"]))
		Story.append(Spacer(1, 12))
		Story.append(Paragraph(code, styles["Normal"]))
		Story.append(Spacer(1, 12))

		if "exception" not in ret:
			if output:
				Story.append(Paragraph("<font size=18>Output</font>", styles["Normal"]))
				Story.append(Spacer(1, 12))
				Story.append(Paragraph(output, styles["Normal"]))
				Story.append(Spacer(1, 12))
		else:
			Story.append(Paragraph("<font size=18>Error</font>", styles["Normal"]))
			Story.append(Spacer(1, 12))
			Story.append(Paragraph(("R code is invalid. ")+ret["exception"]), styles["Normal"])
			Story.append(Spacer(1, 12))

		# Build graphics
		if ret["graphics"]:
			path = os.path.join(PROJECT_ROOT, "languages/r/CACHE/", ret["graphics"]) + ".png"
			Story.append(Paragraph("<font size=18>Graphics</font>", styles["Normal"]))
			Story.append(Spacer(1, 12))
			im = Image(path, 4*inch, 4*inch)
			im.hAlign = 'LEFT'
			Story.append(im)

		# Build document and return path if available
		doc.build(Story, onFirstPage=self.header, onLaterPages=self.header)

		if os.path.isfile(pdf_path):
			return pdf_path
		else:
			return None

	def generate_stu_hash(self):
		"""
		Generates a hash based on user and current date.

		@return int
		"""
		pre_hash_str = self.user.username + datetime.datetime.now().strftime("%Y-%m-%d") \
					   + SECRET_KEY
		hashed_str = sha1(str.encode("{}".format(pre_hash_str)))
		return hashed_str.hexdigest()

	def get_dataset(self):
		"""
		Retrieves FileUpload instance's data from request.

		@return str
		"""
		try:
			fsm = FileSubmissionManager.objects.get(user=self.user, problem=self.problem)
			return fsm.file_upload.get_str_data()
		except:
			return None


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

class FileSubmissionManager(models.Model):
	"""
	Manages unique user-problem combinations for file uploads.
	"""
	user = models.ForeignKey(PCRSUser, on_delete=models.CASCADE)
	file_upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE)
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)


def delete_graph(graph):
	"""
	Deletes the given image from the CACHE of images.

	@param str graph
	@return None
	"""
	if graph:
		path = os.path.join(PROJECT_ROOT, "languages/r/CACHE/", graph) + ".png"
		if os.path.isfile(path):
			os.remove(path)

def load_dataset(data_set):
	"""
	Returns R code for loading in a CSV dataset for R.

	@param str data_set
	@return str
	"""
	total_string = ""
	code_snippet = ""

	rows = data_set.split('\n')
	for row in rows:
		for i in range(len(row)):
			if row[i] != '\n' and row[i] != '"':
				total_string += row[i]
		if row != rows[-1]:
			total_string += '\n'

	code_snippet += "\nlines <- \"" + total_string + "\""
	code_snippet += "\ncon <- textConnection(lines)"
	code_snippet += "\ndata_set <- read.csv(con)"
	code_snippet += "\nclose(con)"

	return code_snippet
