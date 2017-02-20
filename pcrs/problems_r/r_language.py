<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
import os
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
import subprocess
import sys
>>>>>>> pcrs-r: implemented rpy2
=======
>>>>>>> updated requirements.txt
=======
import os
<<<<<<< HEAD
import re
>>>>>>> pcrs-r RSpecifics prototype
=======
>>>>>>> Just execute entire script and redirect output to temporary file
=======
import os
import subprocess
import sys
>>>>>>> pcrs-r: implemented rpy2
=======
>>>>>>> updated requirements.txt
=======
import os
<<<<<<< HEAD
import re
>>>>>>> pcrs-r RSpecifics prototype
=======
>>>>>>> Just execute entire script and redirect output to temporary file
=======
import subprocess
import sys
>>>>>>> pcrs-r: implemented rpy2
=======
>>>>>>> updated requirements.txt
=======
import os
import re
>>>>>>> pcrs-r RSpecifics prototype
=======
>>>>>>> Just execute entire script and redirect output to temporary file
=======
import os
import subprocess
import sys
>>>>>>> pcrs-r: implemented rpy2
=======
>>>>>>> updated requirements.txt
=======
import os
import re
>>>>>>> pcrs-r RSpecifics prototype
from rpy2 import robjects
from hashlib import sha1
from datetime import datetime

import problems.pcrs_languages as languages
from pcrs.settings import PROJECT_ROOT

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
R_TEMPPATH = os.path.join("languages/r/CACHE/")
=======
R_STATICFILES = "" ### PATH TO PLOTS
>>>>>>> pcrs-r: implemented rpy2
=======
R_TEMPPATH = os.path.join(os.path.dirname(__file__), "temporary/")
>>>>>>> pcrs-r RSpecifics prototype
=======
R_TEMPPATH = os.path.join(os.path.dirname(__file__), "CACHE/")
>>>>>>> added models
=======
R_TEMPPATH = os.path.join("../languages/r/CACHE/")
>>>>>>> Installation instructions
=======
R_TEMPPATH = os.path.join("languages/r/CACHE/")
>>>>>>> Implemented graphics in browser
=======
R_STATICFILES = "" ### PATH TO PLOTS
>>>>>>> pcrs-r: implemented rpy2
=======
R_TEMPPATH = os.path.join(os.path.dirname(__file__), "temporary/")
>>>>>>> pcrs-r RSpecifics prototype
=======
R_TEMPPATH = os.path.join(os.path.dirname(__file__), "CACHE/")
>>>>>>> added models
=======
R_TEMPPATH = os.path.join("../languages/r/CACHE/")
>>>>>>> Installation instructions
=======
R_TEMPPATH = os.path.join("languages/r/CACHE/")
>>>>>>> Implemented graphics in browser
=======
R_STATICFILES = "" ### PATH TO PLOTS
>>>>>>> pcrs-r: implemented rpy2
=======
R_TEMPPATH = os.path.join(os.path.dirname(__file__), "temporary/")
>>>>>>> pcrs-r RSpecifics prototype

class RSpecifics(languages.BaseLanguage):
	"""
	Representation of R language (visualizer not supported):
	"""
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> Reverted changes to forms and added a default seed unique to current user
	def run_test(self, user_script, sol_script):
		"""
		@param str user_script
		@param str sol_script

		Return dictionary <ret> containing results of a test run.
		<ret> has the following mapping:
		'test_val' -> <user_script> output (if successful),
		'sol_val' -> <sol_script> output (if successful),
		'graphics' -> path to graphics (if any),
		'sol_graphics' -> path to solution's graphics (if any),
		'passed_test' -> True if <user_script> outputs <expected_val>,
		'exception' -> exception message (if any)
		"""
		# Just a hash we'll use as a unique name
		f_sha = sha1(str.encode("{}".format(user_script+str(datetime.now())))).hexdigest()
		try:
			ret = self.run(user_script)
			solution = self.run(sol_script)

			if "exception" in solution or "exception" in ret:
				ret["passed_test"] = False
				return ret

			ret["passed_test"] = (ret["test_val"] == solution["test_val"])
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
			ret["sol_val"] = solution["test_val"]
=======
>>>>>>> Reverted changes to forms and added a default seed unique to current user
=======
			ret["sol_val"] = solution["test_val"]
>>>>>>> Implemented output visibility field for R problems
=======
			ret["sol_val"] = solution["test_val"]
>>>>>>> Implemented output visibility field for R problems

			if "graphics" in solution.keys():
				ret["sol_graphics"] = solution["graphics"]
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

			# Remove empty lines from R code
			script = self.strip_empty_lines(script)

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


	def strip_empty_lines(self, script):
		"""
		@param str script

		Returns script with all empty lines stripped from it so R code is correct.
		"""
		all_elements = script.split("\n")
		split_elements = [element for element in all_elements if element != ""]

		ret_str = ""
		for i in range(len(split_elements)):
			ret_str += split_elements[i].strip()
			if i != (len(split_elements) - 1):
				ret_str += "\n"

		return ret_str
=======
	def run_test(self, user_script, test_script, args=[], plot=False):
=======
	def run_test(self, user_script, expected_val):
>>>>>>> pcrs-r RSpecifics prototype
=======
	def run_test(self, user_script, sol_script):
>>>>>>> Reverted changes to forms and added a default seed unique to current user
		"""
		@param str user_script
		@param str sol_script

		Return dictionary <ret> containing results of a test run.
		<ret> has the following mapping:
		'test_val' -> <user_script> output (if successful),
		'graphics' -> path to graphics (if any),
		'sol_graphics' -> path to solution's graphics (if any),
		'passed_test' -> True if <user_script> outputs <expected_val>,
		'exception' -> exception message (if any)
		"""
		# Just a hash we'll use as a unique name
		f_sha = sha1(str.encode("{}".format(user_script+str(datetime.now())))).hexdigest()
		try:
			ret = self.run(user_script)
			solution = self.run(sol_script)

			if "exception" in solution or "exception" in ret:
				ret["passed_test"] = False
				return ret

			ret["passed_test"] = (ret["test_val"] == solution["test_val"])

			if "graphics" in solution.keys():
				ret["sol_graphics"] = solution["graphics"]
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

			# Remove empty lines from R code
			script = self.strip_empty_lines(script)

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
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
			ret['test_val'] = str(e)
			ret['passed_test'] = False
			ret['exception'] = str(e)
>>>>>>> pcrs-r: implemented rpy2
=======
			ret["test_val"] = None
=======
=======
			os.remove(path)
>>>>>>> Fixed rendering of graphs
			ret.pop("test_val", None)
>>>>>>> added models
			ret["exception"] = str(e)
<<<<<<< HEAD

<<<<<<< HEAD
<<<<<<< HEAD
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
>>>>>>> pcrs-r RSpecifics prototype
=======
		return ret
>>>>>>> Just execute entire script and redirect output to temporary file
=======
=======
>>>>>>> Added embed functionality in templates and urls. Also implemneted side-by-side graph comparison in problem submission
		return ret
>>>>>>> Installation instructions
=======
	def run_test(self, user_script, test_script, args=[], plot=False):
=======
	def run_test(self, user_script, expected_val):
>>>>>>> pcrs-r RSpecifics prototype
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
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
			ret['test_val'] = str(e)
			ret['passed_test'] = False
			ret['exception'] = str(e)
>>>>>>> pcrs-r: implemented rpy2
=======
			ret["test_val"] = None
=======
=======
			os.remove(path)
>>>>>>> Fixed rendering of graphs
			ret.pop("test_val", None)
>>>>>>> added models
			ret["exception"] = str(e)
<<<<<<< HEAD

<<<<<<< HEAD
<<<<<<< HEAD
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
>>>>>>> pcrs-r RSpecifics prototype
=======
		return ret
>>>>>>> Just execute entire script and redirect output to temporary file
=======
=======
>>>>>>> Added embed functionality in templates and urls. Also implemneted side-by-side graph comparison in problem submission
		return ret
<<<<<<< HEAD
>>>>>>> Installation instructions
=======


	def strip_empty_lines(self, script):
		"""
		@param str script

		Returns script with all empty lines stripped from it so R code is correct.
		"""
		all_elements = script.split("\n")
		split_elements = [element for element in all_elements if element != ""]

		ret_str = ""
		for i in range(len(split_elements)):
			ret_str += split_elements[i].strip()
			if i != (len(split_elements) - 1):
				ret_str += "\n"

		return ret_str
>>>>>>> Stripped code fed into R to work with rpy2
=======
	def run_test(self, user_script, test_script, args=[], plot=False):
=======
	def run_test(self, user_script, expected_val):
>>>>>>> pcrs-r RSpecifics prototype
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
<<<<<<< HEAD
			ret['test_val'] = str(e)
			ret['passed_test'] = False
			ret['exception'] = str(e)
>>>>>>> pcrs-r: implemented rpy2
=======
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
>>>>>>> pcrs-r RSpecifics prototype
