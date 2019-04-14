import unittest
from src.grammar_tester.linkgrammarver import handle_version_response, get_lg_dict_version

text = 'link-grammar-5.5.1 Compiled with: gcc __VERSION__="7.2.0"  OS: linux-gnu __unix__  ' \
       'Standards: __STDC_VERSION__=201112L Configuration (source code): 	CPPFLAGS= 	' \
       'CFLAGS=-D_DEFAULT_SOURCE -std=c11 -D_BSD_SOURCE -D_SVID_SOURCE -D_GNU_SOURCE -D_ISOC11_SOURCE -g -O2 -O3 ' \
       'Configuration (features): 	DICTIONARY_DIR=/home/alex/miniconda3/envs/ull55/share/link-grammar 	' \
       '-DPACKAGE_NAME="link-grammar" -DPACKAGE_TARNAME="link-grammar" -DPACKAGE_VERSION="5.5.1" ' \
       '-DPACKAGE_STRING="link-grammar 5.5.1" -DPACKAGE_BUGREPORT="link-grammar@googlegroups.com" -DPACKAGE_URL="" ' \
       '-DPACKAGE="link-grammar" -DVERSION="5.5.1" -DYYTEXT_POINTER=1 -DSTDC_HEADERS=1 -DHAVE_SYS_TYPES_H=1 ' \
       '-DHAVE_SYS_STAT_H=1 -DHAVE_STDLIB_H=1 -DHAVE_STRING_H=1 -DHAVE_MEMORY_H=1 -DHAVE_STRINGS_H=1 ' \
       '-DHAVE_INTTYPES_H=1 -DHAVE_STDINT_H=1 -DHAVE_UNISTD_H=1 -DHAVE_DLFCN_H=1 -DLT_OBJDIR=".libs/" ' \
       '-DHAVE_STRNDUP=1 -DHAVE_STRTOK_R=1 -DHAVE_ALIGNED_ALLOC=1 -DHAVE_POSIX_MEMALIGN=1 -DHAVE_ALLOCA_H=1 ' \
       '-DHAVE_ALLOCA=1 -DHAVE_FORK=1 -DHAVE_VFORK=1 -DHAVE_WORKING_VFORK=1 -DHAVE_WORKING_FORK=1 -DHAVE_PRCTL=1 ' \
       '-D__STDC_FORMAT_MACROS=1 -D__STDC_LIMIT_MACROS=1 -DHAVE_LOCALE_T_IN_LOCALE_H=1 -DHAVE_STDATOMIC_H=1 ' \
       '-DTLS=__thread -DHAVE_LIBSTDC__=1 -DHAVE_MKLIT=1 -DUSE_SAT_SOLVER=1 -DUSE_WORDGRAPH_DISPLAY=1 ' \
       '-DHAVE_SQLITE=1 -DHAVE_REGEXEC=1 -DHAVE_MAYBE_UNINITIALIZED=1'


class LGVersionTestCase(unittest.TestCase):

    def test_handle_version_response(self):
        self.assertEqual(("5.5.1", "/home/alex/miniconda3/envs/ull55/share/link-grammar"),
                         handle_version_response(text))

    def test_get_lg_dict_version(self):
        self.assertEqual("5.5.0", get_lg_dict_version("tests/test-data/dict/poc-turtle"))


if __name__ == '__main__':
    unittest.main()
