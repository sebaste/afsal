import logging
import multiprocessing
import traceback

from afsal.aux.err import err, err_exit
from afsal.proc import ProcStatus
from afsal.colors.coloring_alg import coloring_alg


def worker(proc_nm, proc_name, text_lines, regexpcs, use_glob_regexps, stdout_is_redirected, text_queue, status_queue):
    p = multiprocessing.current_process()
    p.name = proc_name
    logging.debug(p.name + " started: PID=" + str(p.pid))

    try:
        for i, line in enumerate(text_lines):
            result = coloring_alg(line, regexpcs, use_glob_regexps, stdout_is_redirected)
            if result:
                text_lines[i] = result
        return_str = "".join(text_lines)
        logging.debug(p.name + ": adding processed string to queue")
        text_queue.put( (proc_nm, return_str) )
        text_queue.close()
    except Exception as e:
        tb = traceback.format_exc()
        logging.debug(p.name + ": ERROR: " + tb)
        status_queue.put( (ProcStatus.ERROR, tb) )

    status_queue.put( (ProcStatus.OK, None) )
    status_queue.close()
    logging.debug(p.name + ": ending")


# Split a list into nm_segments sublists, of approximately the same size.
def split_list(l, nm_segments):
    b, n = base_sublist_length, nm_longer_sublists = divmod(len(l), nm_segments)
    pos = base_sublist_length * (nm_segments - nm_longer_sublists)
    return [ l[i * b : (i + 1) * b] for i in range(nm_segments - n) ] + \
            [ l[pos + i * (b + 1) : pos + (i + 1) * (b + 1)] for i in range(n)]


def start_with_subprocs(f_data, f_data_nm_lines, regexpcs, use_glob_regexps, stdout_is_redirected, nm_subprocs):
    try:
        logging.debug("get_all_start_methods()=" + str(multiprocessing.get_all_start_methods()));
        logging.debug("get_start_method()=" + str(multiprocessing.get_start_method()));
    except AttributeError:
        # The methods get_start_method() and get_all_start_methods() were introduced in Python 3.4.
        pass

    logging.debug("nm_subprocs=" + str(nm_subprocs))

    split_f_data = split_list(f_data, nm_subprocs)
    logging.debug("f_data list splitted into " + str(len(split_f_data)) + " segments with length(s) " +
            str([len(x) for x in split_f_data]))

    procs = []
    text_queue = multiprocessing.Queue(nm_subprocs)
    status_queue = multiprocessing.Queue(nm_subprocs)
    for i in range(0, nm_subprocs):
        try:
            proc_name = "Proc-" + str(i)
            t = multiprocessing.Process(target=worker, args=(i, proc_name, split_f_data[i], regexpcs, use_glob_regexps, stdout_is_redirected, text_queue, status_queue,))
            procs.append( (t, proc_name) )
            logging.debug("Starting subprocess " + str(proc_name))
            t.start()
        except Exception as e:
            err_exit(msg=str(e), tb=traceback.format_exc())

    results = []
    for i in range(0, nm_subprocs):
        err_msg = None

        proc_status = status_queue.get()

        if proc_status[0] == ProcStatus.ERROR:
            logging.debug("\"ERROR\" received from " + procs[i][1] + ":\n" + proc_status[1])

            # When an error occured, ignore the queue and terminate alive processes.
            logging.debug("Terminating all subprocesses")
            for j in range(0, nm_subprocs):
                procs[j][0].terminate()
                logging.debug(procs[j][1] + " terminated")

                procs[j][0].join()
                logging.debug("Joined subprocess " + procs[j][1] + ": exitcode=" + str(procs[j][0].exitcode))

            err_exit(msg=procs[i][1] + ": " + proc_status[1])

        # One ProcStatus.OK is received. This means at least one result can be fetched from text_queue.
        text_result = text_queue.get()

        t = procs[ text_result[0] ]
        logging.debug("Joining subprocess " + t[1])
        t[0].join()
        logging.debug("Joined subprocess " + t[1] + ": exitcode=" + str(t[0].exitcode))

        results.append(text_result)

    # Sort based on process number (text segment number).
    sorted_results = sorted(results, key=lambda x: x[0])
    result_str = ""
    for data in sorted_results:
        result_str += data[1]

    return result_str
