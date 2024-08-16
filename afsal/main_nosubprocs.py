from afsal.colors.coloring_alg import coloring_alg


def start_without_subprocs(f_data, f_data_nm_lines, regexpcs, use_glob_regexps, stdout_is_redirected):
    for i, line in enumerate(f_data):
        result = coloring_alg(line, regexpcs, use_glob_regexps, stdout_is_redirected)
        if result:
            f_data[i] = result

    return "".join(f_data)
