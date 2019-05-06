# language-learning/src/grammar_learner/read_files.py                   # 90129
import logging
import os


def check_dir(dir_path, create = False, verbose = 'none'):
    logger = logging.getLogger(__name__ + ".check_dir")
    if os.path.exists(dir_path):
        return True
    else:
        if create:
            os.makedirs(dir_path)
            return True
        # else:
        #     logger.critical(f'No directory {dir_path}')
        #     return False

        raise FileNotFoundError(f'No directory {dir_path}')


def check_dir_files(dir_path, verbose = 'none'):
    logger = logging.getLogger(__name__ + ".check_dir_files")
    files = []
    if dir_path[-1] != '/':
        path = dir_path + '/'
    else:
        path = dir_path
    if os.path.exists(dir_path):
        logger.info(f'Directory {path} exists.')
        for filename in os.listdir(dir_path):
            files.append(path + filename)
            logger.info(filename)
    else:
        # logger.critical(f'No directory {dir_path}')
        raise FileNotFoundError(f'No directory {dir_path}')
    return files


def check_mst_files(input_dir, verbose = 'none'):
    logger = logging.getLogger(__name__ + ".check_mst_files")
    if check_dir(input_dir, create = False, verbose = verbose):
        files = check_dir_files(input_dir, verbose = verbose)
        if len(files) > 0:
            logger.info(files)
            response = {'input files': files}
            for i, file in enumerate(files):
                if os.path.isfile(file):
                    logger.info('File #' + str(i) + f' {file} checked')
                else:
                    logger.critical('File #' + str(i) + f' {file} check failed')
            return files, response
        else:
            logger.critical(f'Input directory {input_dir} is empty')
            return [], {'check_mst_file_error': 'empty input directory'}
    else:
        logger.critical(f'No input directory {input_dir}')
        return [], {'check_mst_file_error': 'no input directory'}


def check_dict(file_path):          # TODO: update this stub            # 90128
    if os.path.isfile(file_path):
        return True
    else: return False


def check_ull(file_path):           # TODO: update this stub            # 90128
    if os.path.isfile(file_path):
        return True
    else: return False


def check_corpus(input_dir, verbose = 'none'):  # TODO: add file tests  # 90129
    if check_dir(input_dir, False, verbose):
        files = check_dir_files(input_dir, verbose)
        if len(files) > 0:
            response = {'input files': files}
            parses = []
            for i, file in enumerate(files):
                if check_ull(file):
                    with open(file, 'r') as f:
                        lines = f.read().splitlines()
                    if len(lines) > 0:
                        parses.extend(lines)
                        parses.extend([])  # empty line
            if len(parses) > 0:
                response.update
                return True
            else: return False
        else: return False
    else: return False


def check_path(par, t = 'else', **kwargs):  # TODO: update stubs...     # 90129
    # default: t = 'else': kwargs[par] is file or dir ⇒ return path
    if 'module_path' in kwargs:
        module_path = kwargs['module_path']
    else:
        return None
    if par in kwargs:
        path = kwargs[par]
        if len(path) == 0:
            path = module_path
        elif 'home' not in path:
            if path[0] != '/':
                path = '/' + path
            path = module_path + path
    else:
        print('"' + par + '" not in kwargs:', kwargs)
        return None
    if 'dir' in t:
        if check_dir(path, True, 'max'):
            return path
        else: return None
    elif 'fil' in t:  # file
        if os.path.isfile(path):
            return path
        else: return None
    elif 'dic' in t:  # 'dict', '.dict'
        if check_dict(path):
            return path
        else: return None
    elif 'cor' in t:  # corpus: dir with file(s)
        # if check_mst_files(path, 'max'): FIXME: returns False ?
        if check_corpus(path):                                          # 90129
            return path
        else: return None
    elif 'ull' in t:  # single corpus file
        if check_ull(path):
            return path
        else: return None
    else:
        if check_dir(path, False, 'none') or os.path.isfile(path):
            return path
        else: return None

# Notes

# 81219 @alex: logger
# 81231 cleanup
# 90128 check_path, stubs: check_dict, check_ull
# TODO: cleanup, check_ull, check corpus dir or/and single file
