# language-learning/src/grammar_learner/read_files.py                   # 80331
import logging
import os


def check_dir(dir_path, create = False, verbose='none'):
    logger = logging.getLogger(__name__ + ".check_dir")
    if os.path.exists(dir_path):
        return True
    else:
        if create:
            os.makedirs(dir_path)
            return True
        else:
            logger.critical(f'No directory {dir_path}')
            return False


def check_dir_files(dir_path, verbose='none'):
    logger = logging.getLogger(__name__ + ".check_dir_files")
    files = []
    if dir_path[-1] != '/':
        path = dir_path + '/'
    else: path = dir_path
    if os.path.exists(dir_path):
        logger.info(f'Directory {path} exists.')
        for filename in os.listdir(dir_path):
            files.append(path+filename)
            logger.info(filename)
    else:
        logger.critical(f'No directory {dir_path}')
    return files


def check_corpus(input_file, verbose='none'):
    logger = logging.getLogger(__name__ + ".check_corpus")

    if os.path.isfile(input_file):
        logger.info(f'File exists: {input_file}')
        logger.debug('Input corpus:\n')
        with open(input_file, 'r') as f:
            lines = f.read().splitlines()
        for line in lines:
            logger.debug(line)
        return True
    else:
        if verbose != 'none':
            logger.info(f'No corpus file: {input_file}')
        return False


def check_mst_files(input_dir, verbose='none'):
    logger = logging.getLogger(__name__ + ".check_mst_files")
    if check_dir(input_dir, create=False, verbose=verbose):
        files = check_dir_files(input_dir, verbose=verbose)
        if len(files) > 0:
            logger.info(files)
            response = {'input files': files}
            for i, file in enumerate(files):
                if check_corpus(file, verbose=verbose):
                    logger.info('File #' + str(i) + f' {file} checked')
                else:
                    logger.critical('File #' + str(i) + f' {file} check failed')
            return files, response
        else:
            logger.critical(f'Input directory {input_dir} is empty')
            return [], {'error': 'empty input directory'}
    else:
        logger.critical(f'No input directory {input_dir}')
        return [], {'error': 'no input directory'}


# Notes

# 81219 @alex: logger
# 81231 cleanup
