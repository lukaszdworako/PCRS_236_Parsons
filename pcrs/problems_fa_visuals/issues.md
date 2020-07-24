Issues with current sprint model

- In pads/Util.py, in `arbitrary_item`, it's `return iter(S).next()` but it should be `next(iter(S))`, as it is in the source code.

- In pads/PartitionRefinement.py, in `__iter__`, it says 

  ```python
  try:
      return self._sets.itervalues() # python 2 compatible code
  except AttributeError:
      return iter(self._sets.values())
  ```

  But PCRS tosses AttributeError, so we need to just have the last line.

- In pads/PartitionRefinement.py, in `freeze`, it says `for S in self._sets.values()` which throws an error because the line `del self._sets[id(S)]` would delete things in the iterator. In the source code, however, it's properly listed as `for S in list(self._sets.values())`.
- I've also made a couple implementation fixes in `Automata.py` compared to `pads/Automata.py`, as there are unimplemented methods in the latter. (These are all included in the push, so no issues there.)
 - implemented `transition()` and `isfinal()` in `class DFA`
 - changed attribute `isfinal` to `final` in `class FiniteAutomaton`

