import rapt

translator = rapt.rapt.Rapt(grammar=rapt.treebrd.grammars.GRAMMARS['Extended Grammar'])
schema = {'ambiguous': ['a', 'a', 'b'], 'gammatwin': ['g1', 'g2'], 'beta': ['b1', 'b2', 'b3'], 'alphatwin': ['a1', 'a2', 'a3'], 'gammaprime': ['g1', 'g2'], 'alphaprime': ['a1', 'a4', 'a5'], 'gamma': ['g1', 'g2'], 'alpha': ['a1', 'a2', 'a3'], 'delta': ['d1', 'd2']}

print(translator.to_syntax_tree(instring="alpha \\theta_join_{alpha.a1 = beta.b1} beta;", schema=schema))
