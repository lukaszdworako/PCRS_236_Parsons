import os
import re
from rpy2 import robjects
from hashlib import sha1
from datetime import datetime

import problems.pcrs_languages as languages
from pcrs.settings import PROJECT_ROOT

R_TEMPPATH = os.path.join(os.path.dirname(__file__), "temporary/")

class RSpecifics(languages.BaseLanguage):
	"""
	Representation of R language (visualizer not supported):
	"""
	def run_test(self, user_script, expected_val):
		"""
		@param str user_script
		@param list[str] expected_val: list of expected outputs

		Return dictionary <ret> containing results of a test run.
		<ret> has the following mapping:
		'test_val' -> list of <user_script> shell outputs (if successful),
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
			# If graphics are created, save it into a temporary file.
			# View should render the .png file, then delete it.
			if not ("try-error" in exec_r("try(dev.copy(png, filename=\"{}.png\"), TRUE)".format(os.path.join(R_TEMPPATH, f_sha))).r_repr()):
				ret["graphics"] = f_sha
			exec_r("graphics.off()")
			ret["passed_test"] = (ret["test_val"] == expected_val)

		except Exception as e:
			ret["exception"] = str(e)
			ret["passed_test"] = False

		return ret
			

	def run(self, script):
		"""
		Returns dictionary <ret> containing output of <script>.
		<ret> has the following mapping:
		'test_val' -> a list of outputs, if successful
		'exception' -> exception message (if any)
		"""
		# Just a hash we'll use as a unique name
		f_sha = sha1(str.encode("{}".format(script+str(datetime.now())))).hexdigest()
		ret = {}
		try:
			exec_r = robjects.r
			# Clear R global environment
			exec_r("rm(list = ls(all.names=TRUE))")
			# Split user script by each command
			# We do this because running the entire script on exec_r saves only the last output
			script = self.join_commands(script)
			script = [self.remove_comments(line) for line in script.split('\n') if line]
			ret["test_val"] = []
			for line in script:
				try:
					# Suppress automatic shell messages
					exec_r("STDOUT_RET_VAR<-capture.output({})".format(line))
					stdout = exec_r("{}".format("STDOUT_RET_VAR")).r_repr()
					if stdout != "character(0)":
						ret["test_val"].append(stdout[1:-1])
				except:
					# capture.output will raise its own exception for some non-problematic expressions (e.g. "1")
					# Execute the line to check if it's really problematic
					exec_r(line)
					continue
			# Close graphics
			exec_r("graphics.off()")
		except Exception as e:
			ret["test_val"] = None
			ret["exception"] = str(e)

		return ret

	def join_commands(self, script):
		"""
		Scans <script> for multi-line commands and joins them back together.
		Returns modified <script>
		"""
		# TO-DO: parse for multi-line code
		return script

	def remove_comments(self, line):
		"""
		Remove comments from <line> of R code and return <line>.
		"""
		return line[:line.index('#')].strip() if '#' in line else line