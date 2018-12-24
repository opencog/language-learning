#language-learning/src/grammar_learner/read_files.py #80331
import os


def check_dir(dir_path, create = False, verbose='none'):
    if os.path.exists(dir_path):
        if verbose in ['max', 'debug']:
            print('Directory', dir_path, 'exists.')
        return True
    else:
        if create:
            os.makedirs(dir_path)
            if verbose in ['max', 'debug']:
                print('Directory', dir_path, 'created.')
            return True
        else:
            if verbose != 'none':
                print('No directory', dir_path)
            return False


def check_dir_files(dir_path, verbose='none'):
    files = []
    if dir_path[-1] != '/':
        path = dir_path + '/'
    else: path = dir_path
    if os.path.exists(dir_path):
        if verbose in ['max', 'debug']:
            print('Directory', path, 'exists.')
        for filename in os.listdir(dir_path):
            files.append(path+filename)
            if verbose in ['max', 'debug']:
                print(filename)
    else:
        if verbose != 'none':
            print('No directory', dir_path)
    return files


def check_corpus(input_file, verbose='none'):
    if os.path.isfile(input_file):
        if verbose in ['max','debug']:
            print('File exists:', input_file)
        if verbose == 'debug':
            print('Input corpus:\n')
            with open(input_file, 'r') as f:
                lines = f.read().splitlines()
            for line in lines: print(line)
        return True
    else:
        if verbose != 'none':
            print('No corpus file', input_file)
        return False


def check_mst_files(input_dir, verbose='none'):
    if check_dir(input_dir, create=False, verbose=verbose):
        files = check_dir_files(input_dir, verbose=verbose)
        if len(files) > 0:
            if verbose in ['max', 'debug']:
                print(files)
            response = {'input files': files}
            for i,file in enumerate(files):
                if check_corpus(file, verbose=verbose):
                    if verbose in ['max', 'debug']:
                        print('File #'+str(i), file, 'checked')
                else:
                    if verbose != 'none':
                        print('File #'+str(i), file, 'check failed')
            return files, response
        else:
            if verbose != 'none':
                print('Input directory', input_dir, 'is empty')
            return [], {'error': 'empty input directory'}
    else:
        if verbose != 'none':
            print('No input directory', input_dir)
        return [], {'error': 'no input directory'}
