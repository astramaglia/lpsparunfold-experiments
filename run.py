import pathlib
import subprocess
import os.path
import logging
import sys
import time
import yaml
import re

logging.basicConfig(level=logging.INFO)

USELIMITS = True
# Timeout in Seconds
TIMEOUT = 3600
# Memlimit in KBytes
MEMLIMIT = 64*1024*1024

_TIMEOUTSCRIPT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "timeout")
# Path to MCRL2_master version containing the default version of Groote and Lisser of lpsparunfold
mcrl2_master_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tools/MCRL2_master/install/bin/')

# Path to MCRL2_parunfold version containing the updated version of lpsparunfold

mcrl2_parunfold_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tools/MCRL2_parunfold/install/bin/')

# path to folder 'models'
models_path = os.path.abspath(os.path.join(os.path.split(__file__)[0], 'models'))

# Dictionary with models.
# key: model name
# values: list of pairs with types to be unfolded and number of times to unfold.
models = {
    "tictactoe3-3": [("Board", 3), ("Row", 3)],
    "fourinarow3-4": [("Board", 3), ("Row", 4)],
    "fourinarow3-5": [("Board", 3), ("Row", 5)],
    "fourinarow4-3": [("Board", 4), ("Row", 3)],
    "fourinarow4-4": [("Board", 4), ("Row", 4)],
    "fourinarow4-5": [("Board", 4), ("Row", 5)],
    "fourinarow5-3": [("Board", 5), ("Row", 3)],
    "fourinarow5-4": [("Board", 5), ("Row", 4)],
    "fourinarow5-5": [("Board", 5), ("Row", 5)],
    "swp2-2": [("DBuf", 2), ("BBuf", 2)],
    "swp2-4": [("DBuf", 2), ("BBuf", 2)],
    "swp2-6": [("DBuf", 2), ("BBuf", 2)],
    "swp2-8": [("DBuf", 2), ("BBuf", 2)],
    "swp4-2": [("DBuf", 4), ("BBuf", 4)],
    "swp4-4": [("DBuf", 4), ("BBuf", 4)],
    "swp4-6": [("DBuf", 4), ("BBuf", 4)],
    "swp4-8": [("DBuf", 4), ("BBuf", 4)],
    "swp8-2": [("DBuf", 8), ("BBuf", 8)],
    "onoff": [("Sys", 1)],
    "cylinder": [("List(State)", 4), ("State", 1)],
    "sla7": [("List(Message)", 7)],
    "sla10": [("List(Message)", 10)],
    "sla13": [("List(Message)", 13)],
    "wms": [("List(Job)", 1)]
}

# constant to change name of LPS file
static_hint = 'static_only'
# hint to track output from MCRL2_master with default case placement
default_master = 'default_master'
# hint to track output from MCRL2_parunfold with default case placement
default_parunfold = 'default_parunfold'
# hint to track output from MCRL2_parunfold with alternative case placement
alternative_parunfold = 'alternative_parunfold'

D = {}
list_tools = [] # the names of the tools to be appended here are given in such a way to be unique since they are then zipped as values in a dictionary
list_times = []


class ToolException(Exception):
    def __init__(self, tool, exitcode, result):
        Exception.__init__(self)
        self.__result = result
        self.__ret = exitcode
        self.__cmdline = ' '.join(tool)

    def __str__(self):
        return 'The commandline "{0}" failed with exit code "{1}".\nStandard error and output:\n{2}\n'.format(
            self.__cmdline, self.__ret, self.__result['err'], self.__result['out'])


class Timeout(Exception):
    def __init__(self, cmdline, result):
        super(Timeout, self).__init__()
        self.__cmdline = ' '.join(cmdline)
        self.result = result

    def __str__(self):
        return 'The commandline "{0}" timed out'.format(self.__cmdline)


class OutOfMemory(Exception):
    def __init__(self, cmdline, result):
        super(OutOfMemory, self).__init__()
        self.__cmdline = ' '.join(cmdline)
        self.result = result


def split_input_filename(input_path):
    """Split the input path into directory and basename of the file"""
    dirname, file = os.path.split(input_path)
    base, ext = os.path.splitext(file)
    return dirname, base


def mcrl2_filepath(dirname, root):
    """Returns dirname/root.mcrl2"""
    mcrl2_filename = "{}.mcrl2".format(root)
    return os.path.join(dirname, mcrl2_filename)


def lps_filepath(dirname, root, hint=None):
    """Returns dirname/root(.hint).lps. .hint is omitted if hint is none"""
    if hint:
        return os.path.join(dirname, "{}.{}.lps".format(root, hint))
    else:
        return os.path.join(dirname, "{}.lps".format(root))


def run_command(mcrl2_path, tool, options, input_file, output_file = None, timeout=None, memlimit=None):
    data = {}
    data["mcrl2_path"] = mcrl2_path
    data["tool"] = tool
    data["options"] = options
    data["input_file"] = input_file

    output_file_arg = []
    if output_file:
        data["output_file"] = output_file
        output_file_arg = [output_file]

    command = [os.path.join(mcrl2_path, tool)] + options + [input_file] + output_file_arg

    start_time = time.time()  # Start time of the command execution

    timeoutcmd = []
    if (timeout is not None or memlimit is not None) and USELIMITS:
        if not os.path.exists(_TIMEOUTSCRIPT):
            logging.error('The script {0} does not exists, cannot run without it'.format(_TIMEOUTSCRIPT))
            raise Exception('File {0} not found'.format(_TIMEOUTSCRIPT))

        timeoutcmd += [_TIMEOUTSCRIPT, '--confess', '--no-info-on-success']
        if timeout is not None:
            timeoutcmd += ['-t', str(timeout)]
        if memlimit is not None:
            timeoutcmd += ['-m', str(memlimit)]

        command = timeoutcmd + command

    # try:
    proc = subprocess.run(command, check=False, capture_output=True, text=True)
    # except (subprocess.CalledProcessError):

    if proc.returncode != 0:
        # Filter the output to see whether we exceeded time or memory:
        TIMEOUT_RE = 'TIMEOUT CPU (?P<cpu>\d+[.]\d*) MEM (?P<mem>\d+) MAXMEM (?P<maxmem>\d+) STALE (?P<stale>\d+)'
        m = re.search(TIMEOUT_RE, str(proc.stderr), re.DOTALL)
        if m is not None:
            data['times'] = 'timeout'
            raise Timeout(command, data)

        MEMLIMIT_RE = 'MEM CPU (?P<cpu>\d+[.]\d*) MEM (?P<mem>\d+) MAXMEM (?P<maxmem>\d+) STALE (?P<stale>\d+)'
        m = re.search(MEMLIMIT_RE, str(proc.stderr), re.DOTALL)
        if m is not None:
            data['memory'] = 'outofmemory'
            raise OutOfMemory(command, data)

        # raise ToolException(command, proc.returncode, {'err':proc.stderr, 'out': proc.stdout})
        raise ToolException(command, proc.returncode, {'err': proc.stderr, 'out': proc.stdout})

    end_time = time.time()

    elapsed_time = end_time - start_time

    if "lpsreach" in os.path.join(mcrl2_path, tool):
        result = re.match(r"number of states = ([+\-]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+\-]?\d+)?) \(.*$", str(proc.stdout))
        print(str(proc.stdout))
        data["size"] = result.group(1)
    logging.debug(proc.stderr)

    data["time"] = elapsed_time

    return data


def linearise(dirname, root, mcrl2=mcrl2_master_path):
    mcrl2file = mcrl2_filepath(dirname, root)
    lpsfile = lps_filepath(dirname, root)

    if "gantry" in root:
        logging.info("Translating mCRL2 specification {} to LPS {}".format(mcrl2file, lpsfile))
        data = run_command(mcrl2, "mcrl22lps", ["-b"], mcrl2file, lpsfile)
    else:
        logging.info("Translating mCRL2 specification {} to LPS {}".format(mcrl2file, lpsfile))
        data = run_command(mcrl2, "mcrl22lps", [], mcrl2file, lpsfile)

    logging.info("Successfully finished translating mCRL2 specification.")

    if 'tictactoe' in root:
        preprocessing(dirname, root, mcrl2, "Nat")
    if 'fourinarow' in root:
        preprocessing(dirname, root, mcrl2, "Pos")

    return {"mcrl22lps": data}


def preprocessing(dirname, root, mcrl2=mcrl2_master_path, sorts=""):
    lpsfile = lps_filepath(dirname, root)
    logging.info("Applying preprocessing tools to LPS {}".format(lpsfile))

    data = run_command(mcrl2, "lpssuminst", ["-v", "-s{}".format(sorts)], lpsfile, lpsfile)
    logging.info("Successfully finished preprocessing.")
    return {"lpssuminst": data}


def run_static_analysis_tools(dirname, root, mcrl2=mcrl2_master_path, hint=static_hint):
    data = {}

    logging.info("Applying static analysis tools to LPS {}".format(lps_filepath(dirname, root)))
    if hint in [default_master, default_parunfold, alternative_parunfold]:
        replace_hint = hint
    else:
        replace_hint = ''

    data["lpssuminst"] = run_command(mcrl2, "lpssuminst", ["-v", "-f"], lps_filepath(dirname, root, replace_hint),
                                     lps_filepath(dirname, root, hint))

    data["lpsconstelm"] = run_command(mcrl2, "lpsconstelm", ["-vsft"], lps_filepath(dirname, root, hint),
                                      lps_filepath(dirname, root, hint))

    data["lpsparelm"] = run_command(mcrl2, "lpsparelm", ["-v"], lps_filepath(dirname, root, hint), lps_filepath(dirname, root, hint))

    data["lpssumelm"] = run_command(mcrl2, "lpssumelm", ["-v"], lps_filepath(dirname, root, hint), lps_filepath(dirname, root, hint))

    logging.info("Successfully finished applying static analysis tools to LPS.")
    return data


def run_parunfold(dirname, root, mcrl2_path, alternative_case_placement=False):
    alt_arg = []

    # if the version is master then run unfolding as of Groote Lisser
    if mcrl2_path == mcrl2_master_path:
        assert(not alternative_case_placement)  # Master does not support alternative case placement
        hint = default_master
        logging.info("Default unfolding from master + static analysis tools")
    elif alternative_case_placement:
        # if the version of mcrl2 is parunfold then run the unfolding both with Groote Lisser method and with new unfolding
        # new unfolding
        hint = alternative_parunfold
        logging.info("Alternative unfolding from parunfold + static analysis tools")
        alt_arg = ["-a"]
    else:
        # default unfolding
        hint = default_parunfold
        logging.info("Default unfolding from parunfold + static analysis tools")

    # Set up input file and output file
    input_file = lps_filepath(dirname, root)
    output_file = lps_filepath(dirname, root, hint)

    # Log data that is shared for all runs of parunfold
    parunfold_data = {"mcrl2_path": mcrl2_path,
            "input_file": input_file,
            "output_file": output_file,
            "unfoldings": []}

    # Unfold each of the sorts in the list
    # Note that we do not store the intermediate LPS files
    proc_prev = None  # Previous process that was run.
    proc = None
    for (sort, n) in models[root]:
        print("sort: {}, n: {}".format(sort, n))

        input_arg = [input_file] if proc_prev is None else []
        options = ["-v"] + alt_arg + ["-s{}".format(sort), "-n{}".format(n)]

        command = [os.path.join(mcrl2_path, "lpsparunfold")] + options + input_arg

        start_time = time.time()  # Start time of the command execution
        proc = subprocess.Popen(command, stdin=None if proc_prev is None else proc_prev.stdout, stdout=subprocess.PIPE)
        logging.debug(proc.stderr)
        end_time = time.time()
        elapsed_time = end_time - start_time

        if proc_prev is not None:
            proc_prev.stdout.close()
        proc_prev = proc

        # Log data for this round of parunfold
        sort_data = {"options": options, "time": elapsed_time}
        parunfold_data["unfoldings"] += [sort_data]

    output = proc.communicate()[0]
    with open(output_file, 'wb') as of:
        of.write(output)
        of.close()

    data = {"lpsparunfold": parunfold_data}

    sa_data = run_static_analysis_tools(dirname, root, mcrl2_path, hint)
    data.update(sa_data)

    return data


def symbolic_reachability(dirname, root, mcrl2=mcrl2_master_path):
    lpsreach_data = {}
    for hint in [static_hint, default_master, default_parunfold, alternative_parunfold]:
        lps_file = lps_filepath(dirname, root, hint)

        logging.info("Applying symbolic reachability to LPS {}".format(lps_file))
        try:
            print("Trying")
            lpsreach_data[hint] = run_command(mcrl2, "lpsreach", ["-v", "--print-exact","-m64", "--cached", "--groups=simple"], lps_file, timeout=TIMEOUT, memlimit=MEMLIMIT)
            logging.info("Successfully applied symbolic reachability")

        except (ToolException, Timeout, OutOfMemory) as e:
            print("This run crashed")
            lpsreach_data[hint] = e.result
            logging.error("Failed to perform symbolic reachability because {}".format(e))

    return lpsreach_data


def main():
    data = {}

    for keys in models.keys():
        data[keys] = {}

        input_file = os.path.join(os.path.split(__file__)[0], 'models', pathlib.Path(models_path), keys)
        path, filename = split_input_filename(input_file)

        # step 1
        data[keys]["mcrl22lps"] = linearise(path, filename)

        # step 2
        data[keys][static_hint] = run_static_analysis_tools(path, filename)

        # step 3 unfolding using MCRL2_master
        data[keys][default_master] = run_parunfold(path, filename, mcrl2_master_path)

        # step 4 unfolding using MCRL2_parunfold
        data[keys][default_parunfold] = run_parunfold(path, filename, mcrl2_parunfold_path)
        data[keys][alternative_parunfold] = run_parunfold(path, filename, mcrl2_parunfold_path, True)

        # step 5 symbolic reachability
        lpsreach_data = symbolic_reachability(path, filename)
        for (k, v) in lpsreach_data.items():
            data[keys][k]["reachability"] = v



    with open(sys.argv[1], 'w') as file:
        yaml.safe_dump(data, file, sort_keys=False, default_flow_style=False)


if __name__ == "__main__":
    main()
