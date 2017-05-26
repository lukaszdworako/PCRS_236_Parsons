import os
from rpy2 import robjects
from hashlib import sha1
from datetime import datetime

import problems.pcrs_languages as languages

R_TEMPPATH = os.path.join("languages/r/CACHE/")

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
		try:
			exec_r = robjects.r
			ret = self.run(user_script)

			if "exception" in ret:
				ret["passed_test"] = False
				return ret

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
		'test_val' -> <script> output, if successful,
		'graphics' -> path to graphics (if any),
		'exception' -> exception message (if any)
		"""
		# Just a hash we'll use as a unique name
		f_sha = sha1(str.encode("{}".format(script+str(datetime.now())))).hexdigest()
		ret = {}
		try:
			# Path to temporary .txt file for output of script
			path = os.path.join(R_TEMPPATH, f_sha) + ".txt"
			# Path to temporary .png file for graphics of script
			g_path = path[:-4] + ".png"

			exec_r = robjects.r
			# Clear R global environment and redirect stdout to temporary .txt file
			exec_r("rm(list = ls(all.names=TRUE))")
			exec_r("sink(\"{}\")".format(path))

			# Sets the graphical output to a temporary file
			exec_r("png(\"{}\")".format(g_path)) # output to pdf for multiple graphs

			# Execute script
			exec_r(script)

			# Shutdown current device
			exec_r("dev.off()")

			exec_r("sink()") # prevent sink stack from getting full
			# Read and remove temporary .txt
			with open(path, "r") as f:
				ret["test_val"] = f.read()
			os.remove(path)

			# If graphics exist, return the path
			if os.path.isfile(g_path):
				ret["graphics"] = f_sha
			else:
				ret["graphics"] = None
		except Exception as e:
			os.remove(path)
			ret.pop("test_val", None)
			ret["exception"] = str(e)
		return ret
