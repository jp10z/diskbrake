from subprocess import Popen, PIPE
from .logger import Logger

def run_sh(script):
    Logger.data("RUN_SH SCRIPT: {}".format(script))
    session = Popen([script], stdout=PIPE, stderr=PIPE, shell = True)
    stdout, stderr = session.communicate()

    script_results = {}

    script_results["errors"] = str(stderr).strip('\n').strip()
    script_results["results"] = stdout.decode('utf-8').strip('\n').strip()

    if script_results["errors"] == "" or script_results["errors"] == "b''":
        script_results["errors"] = None
    else:
        Logger.error("RUN_SH ERRORS: {}".format(script_results["errors"]))
    if script_results["results"] == "":
        script_results["results"] = None
    else:
        Logger.data("RUN_SH RESULTS: {}".format(script_results["results"]))

    return script_results