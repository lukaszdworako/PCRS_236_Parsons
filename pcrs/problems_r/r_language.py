import os
import subprocess
import sys
from rpy2 import robjects
from hashlib import sha1
from datetime import datetime

import problems.pcrs_languages as languages

R_STATICFILES = "" ### PATH TO PLOTS

class RSpecifics(languages.BaseLanguage):
	"""
	Representation of R language (visualizer not supported):
	"""
	def run_test(self, user_script, test_script, args=[], plot=False):
		"""
		@param list args: list of input arguments into wrapper main function
		@param bool plot: True if output includes a plot

		Return dictionary <ret> containing results of a test run.
		<ret> has the following mapping:
		'test_val' -> output of <user_script>,
		'plot' -> path to plot (if any),
		'passed_test' -> True if, given <args>,
			output of <user_script> is equal to output of 
			<test_script> - otherwise False
		'exception' -> exception message, if there are any

		=== Preconditions ===
		Script arguments must be wrapped in a main() function
		with same number of arguments as test_input
		i.e.
		main <- function(...) {
			... BODY HERE ...
		}
		"""
		ret = {}
		try:
			exec_r = robjects.r
			# Clear R global environment
			exec_r("rm(list = ls(all.names=TRUE))")
			user_res = exec_r(user_script)(*args)
			ret['test_val'] = str(user_res)
			if plot:
				f_sha = sha1(str.encode("{}".format(user_script+str(datetime.now())))).hexdigest()
				# View should render the .png file, then delete it.
				exec_r("dev.copy(png, {}\{}.png)".format(R_STATICFILES, f_sha))
				exec_r("dev.off()")
			exec_r("rm(list = ls(all.names=TRUE))")
			test_res = exec_r(test_script)(*args)
			ret['passed_test'] = (ret['test_val'] == str(test_res))
		except Exception as e:
			ret['test_val'] = str(e)
			ret['passed_test'] = False
			ret['exception'] = str(e)