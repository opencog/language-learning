# POC-Turtle-6-Tests.ipynb 2018-03-09

def test_turtle_rules(lg_rule_list, test_data_path, create='False'):
    import pickle
    if len(lg_rule_list) == 6:
        file = test_data_path + 'turtle_6c_lg_rules.pkl'
    elif len(lg_rule_list) == 8:
        file = test_data_path + 'turtle_8c_lg_rules.pkl'
    else:
        return False, 'No reference rules for ' \
            + str(len(lg_rule_list)) + ' clusters'
    if create:
        with open(file, 'wb') as f: pickle.dump(lg_rule_list, f)
    with open(file, 'rb') as f: reference = pickle.load(f)
    if lg_rule_list == reference: return True, file, reference
    else: return False, file, reference


def test_turtle_word_categories(lg_rule_list, test_data_path, create='False'):
    import pickle
    if len(lg_rule_list) == 6:
        file = test_data_path + 'turtle_6c_categories.pkl'
    elif len(lg_rule_list) == 8:
        file = test_data_path + 'turtle_8c_categories.pkl'
    else:
        return False, 'No reference rules for ' \
            + str(len(lg_rule_list)) + ' clusters'
    categories = [[x[0],x[1]] for x in lg_rule_list]
    if create:
        with open(file, 'wb') as f: pickle.dump(categories, f)
    with open(file, 'rb') as f: reference = pickle.load(f)
    if categories == reference: return True, file, reference
    else: return False, file, reference


def test_turtle_grammar(lg_rule_list, test_data_path, create='False'):
    import pickle
    if len(lg_rule_list) == 6:
        file = test_data_path + 'turtle_6c_grammar.pkl'
    elif len(lg_rule_list) == 8:
        file = test_data_path + 'turtle_8c_grammar.pkl'
    else:
        return False, 'No reference rules for ' \
            + str(len(lg_rule_list)) + ' clusters'
    grammar = [[x[0],x[1],x[4]] for x in lg_rule_list]
    if create:
        with open(file, 'wb') as f: pickle.dump(grammar, f)
    with open(file, 'rb') as f: reference = pickle.load(f)
    if grammar == reference: return True, file, reference
    else: return False, file, reference
