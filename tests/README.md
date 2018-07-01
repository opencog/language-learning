# Integration tests
Pytest test file names: `test_name.py` or `name_test.py`  
Preferred location: `\language-learning\tests`  
Test data files location: `\language-learning\tests\data`  
Grammar Learner POC.0.5 (proof-of-concept, June 2018) integration test:  `grammar_learner_05_test.py`  
## Run tests
```
cd ~/language-learning
source activate ull4
pytest tests/grammar_learner_05_test.py
```
## Attn: pytest and unittest files
pytest treats any .py file starting from `test_` or ending with `_test` as pytest files ans tries to run all of them when started with no file name argument.  
**Fails to run unittest files**.
---
