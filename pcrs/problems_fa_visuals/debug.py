import automata as fa

reglang = fa.RegExp('a*')
dfa_ans = fa.DFA()
dfa_ans.transitions = {(1, 'a'): 1}
dfa.initial = 1
dfa.accepting = [1]
dfa.alphabet = ['a']
print(reglang.asDFA() == dfa_ans)
# print(reg)