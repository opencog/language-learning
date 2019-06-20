import unittest

from src.pipeline.pipelinetree import PipelineTreeNode2, build_tree, prepare_parameters

config = [
    {
        'component': 'grammar-learner',
        'common-parameters': {
            'space': 'connectors-DRK-connectors',
            'input_parses': '~/data/parses/POC-Turtle/LG/parses',
            'output_categories': '%LEAF',
            'output_grammar': '%LEAF',
            'output_statistics': '',
            'cluster_criteria': 'silhouette',
            'cluster_level': 1,
            'tmpath': '/var/tmp/',
            'verbose': 'min',
            'categories_generalization': 'off',
            'context': 1,
            'word_space': 'vectors',
            'clustering': ['kmeans', 'kmeans++', 18],
            'cluster_range': [2, 50, 9],
            'grammar_rules': 2,
            'temp_dir': ''
        },
        'specific-parameters': [
            {'!space': 'connectors-DRK-connectors', 'wtf': 'MST-fixed-manually', 'left_wall': 'LW', 'period': True},
            {'!space': 'connectors-DRK-connectors', 'wtf': 'MST-fixed-manually', 'left_wall': '', 'period': False}
        ]
    },
    {
        'component': 'grammar-tester',
        'common-parameters': {
            'input_grammar': '%PREV/',
            'corpus_path': '%ROOT/aging3.txt',
            'output_path': '%PREV/',
            'linkage_limit': '1000',
            'rm_grammar_dir': True,
            'use_link_parser': True,
            'ull_input': True,
            'ignore_left_wall': True,
            'ignore_period': True,
            'calc_parse_quality': True
        },
        'specific-parameters': [
            {'parse_format': 'ull'},
            {'parse_format': 'diagram', "follow_exec_path": False},
            {'parse_format': 'postscript', "follow_exec_path": False},
            {'parse_format': 'constituent', "follow_exec_path": False}
        ]
    }
]
# {
#     'component': 'dash-board',
#     'common-parameters': {
#         'input_grammar': '%PREV/',
#         'corpus_path': '%ROOT/aging3.txt',
#         'output_path': '%PREV/',
#         'linkage_limit': '1000',
#         'rm_grammar_dir': True,
#         'use_link_parser': True,
#         'ull_input': True,
#         'ignore_left_wall': True,
#         'ignore_period': True,
#         'calc_parse_quality': True
#     },
#     'specific-parameters': [
#         {'row': '1', 'col': '8', 'value': '%PREV.PA'},
#         {'row': '2', 'col': '9', 'value': '%PREV.PQ'},
#     ]
# }


class PipelineTreeTestCase(unittest.TestCase):

    @unittest.skip
    def test_init(self):
        root = PipelineTreeNode2("grammar-learner", {"space": "cDRKc"}, {"input_parses": "~/data/parses/poc-turtle"})
        self.assertEqual("grammar-learner", root._component_name)
        self.assertEqual({"space": "cDRKc"}, root._specific_parameters)
        self.assertEqual({"input_parses": "~/data/parses/poc-turtle"}, root._common_parameters)
        self.assertEqual({}, root._environment)

    @unittest.skip
    def test_add_siblings(self):
        root = PipelineTreeNode2("grammar-learner", {"space": "cDRKc"}, {"input_parses": "~/data/parses/poc-turtle"})
        root.add_sibling(PipelineTreeNode2("grammar-tester", {"A": "a"}))
        root.add_sibling(PipelineTreeNode2("grammar-tester", {"B": "b"}))
        root.add_sibling(PipelineTreeNode2("grammar-tester", {"C": "c"}))
        self.assertEqual(3, len(root._siblings))

    @unittest.skip
    def test_traverse(self):
        root = PipelineTreeNode2(0, "grammar-learner", {"space": "cDRKc"}, {"input_parses": "~/data/parses/poc-turtle"})
        PipelineTreeNode2(1, "grammar-tester", {"A": "a"}, None, None, root)
        PipelineTreeNode2(1, "grammar-tester", {"B": "b"}, None, None, root)
        node = PipelineTreeNode2(1, "grammar-tester", {"C": "c"}, None, None, root)
        PipelineTreeNode2(2, "grammar-tester", {"CC": "cc"}, None, None, node)
        # root.traverse(lambda n: print(n._component_name), root.root)
        PipelineTreeNode2.traverse_all(lambda n: print("\t"*n.seq_no+n._component_name+": "+str(n._specific_parameters)))
        self.assertEqual(True, True)

    def test_prepare_parameters(self):
        p, e = prepare_parameters(None, {"path_to_somewhere": "%ROOT/abc", "another_path": "%LEAF"},
                                  {"path_to_elsewhere": "%ROOT/efg", "X": "xx", "n": 1},
                                  {"ROOT": "~/data/2018-09-01"}, "%", True)
        # print(p, e, sep="\n")

        self.assertEqual(p["path_to_somewhere"], "~/data/2018-09-01/abc")
        self.assertEqual(p["path_to_elsewhere"], "~/data/2018-09-01/efg")
        self.assertEqual(e["LEAF"], "~/data/2018-09-01/_X:xx_n:1")

    # @unittest.skip
    def test_build_tree(self):

        globals = {"ROOT": "~/data/2018-09-01"}
        roots = build_tree(config, globals)

        # PipelineTreeNode2.traverse_all(lambda n: print("\t"*n.seq_no+n._component_name))
        PipelineTreeNode2.traverse_all(lambda n: print("\t"*n.seq_no+n._component_name+": "+str(n._parameters)))

        print(globals)

        self.assertEqual(True, True)

    @unittest.skip
    def test_traverse_all(self):
        tp = [
            PipelineTreeNode2(0, "text-parser", {"dummy": "1"}),
            PipelineTreeNode2(0, "text-parser", {"dummy": "2"}),
            PipelineTreeNode2(0, "text-parser", {"dummy": "3"})
        ]

        for parent in tp:
            parent.add_sibling(PipelineTreeNode2(1, "grammar-learner", {"dummy": "a"}, None, None, parent))
            parent.add_sibling(PipelineTreeNode2(1, "grammar-learner", {"dummy": "b"}, None, None, parent))
            parent.add_sibling(PipelineTreeNode2(1, "grammar-learner", {"dummy": "c"}, None, None, parent))

        print(PipelineTreeNode2.roots)

        PipelineTreeNode2.traverse_all(lambda p, e: print(p))

        self.assertEqual(True, True)

