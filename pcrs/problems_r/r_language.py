import os
from rpy2 import robjects
from hashlib import sha1
from datetime import datetime

import problems.pcrs_languages as languages

R_TEMPPATH = os.path.join(os.path.dirname(__file__), "temporary/")

class RSpecifics(languages.BaseLanguage):
	"""
	Representation of R language (visualizer not supported):
	"""
	def run_test(self, user_script, expected_val):
		"""
		@param str user_script
		@param str expected_val: expected output

		Return dictionary <ret> containing results of a test run.
		<ret> has the following mapping:
		'test_val' -> <user_script> output (if successful),
		'graphics' -> path to graphics (if any),
		'passed_test' -> True if <user_script> outputs <expected_val>
		'exception' -> exception message (if any)
		"""
		# Just a hash we'll use as a unique name
		f_sha = sha1(str.encode("{}".format(user_script+str(datetime.now())))).hexdigest()
		ret = {}
		try:
			exec_r = robjects.r
			test_val = self.run(user_script)
			if "exception" in test_val:
				ret["passed_test"] = False
				ret["exception"] = test_val["exception"]
				return ret
			ret["test_val"] = test_val["test_val"]
			ret["passed_test"] = (ret["test_val"] == expected_val)
		except Exception as e:
			ret["exception"] = str(e)
			ret["passed_test"] = False

		return ret
			

	def run(self, script):
		"""
		@param str script

		Returns dictionary <ret> containing output of <script>.
		<ret> has the following mapping:
		'test_val' -> <script> output, if successful
		'exception' -> exception message (if any)
		"""
		# Just a hash we'll use as a unique name
		f_sha = sha1(str.encode("{}".format(script+str(datetime.now())))).hexdigest()
		ret = {}
		try:
			exec_r = robjects.r
			# Clear R global environment and redirect stdout to temporary .txt file
			exec_r("rm(list = ls(all.names=TRUE))")
			exec_r("sink(\"{}.txt\")".format(os.path.join(R_TEMPPATH, f_sha)))
			# Execute script
			exec_r(script)
			# If graphics exist, save it into a temporary file.
			# View should render the .png file, then delete it.
			if not ("try-error" in exec_r("try(dev.copy(png, filename=\"{}.png\"), TRUE)".format(os.path.join(R_TEMPPATH, f_sha))).r_repr()):
				ret["graphics"] = f_sha
			exec_r("graphics.off()")
			# Read and remove temporary .txt
			with open("{}.txt".format(os.path.join(R_TEMPPATH, f_sha)), "r") as f:
				ret["test_val"] = f.read()
			os.remove("{}.txt".format(os.path.join(R_TEMPPATH, f_sha)))
		except Exception as e:
			ret["test_val"] = None
			ret["exception"] = str(e)

		return ret