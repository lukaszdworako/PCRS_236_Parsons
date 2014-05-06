# Online Python Tutor
# Copyright (C) 2010-2011 Philip J. Guo (philip@pgbovine.net)
# https://github.com/pgbovine/OnlinePythonTutor/
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Given an arbitrary piece of Python data, encode it in such a manner
# that it can be later encoded into JSON.
#   http://json.org/
#
# We use this function to encode run-time traces of data structures
# to send to the front-end.
#
# Format:
#   * circular reference - ['CIRCULAR_REF', unique_id]
#   * int, float, bool - unchanged
#     (json.dumps encodes these fine verbatim)
#   * None     - ['NONETYPE', unique_id, str]
#   * str      - ['STRING', unique_id, str] 
#   * list     - ['LIST', unique_id, elt1, elt2, elt3, ..., eltN]
#   * tuple    - ['TUPLE', unique_id, elt1, elt2, elt3, ..., eltN]
#   * set      - ['SET', unique_id, elt1, elt2, elt3, ..., eltN]
#   * dict     - ['DICT', unique_id, [key1, value1], [key2, value2], ..., [keyN, valueN]]
#   * function - ['FUNCTION', unique_id, functionName] 
#   * class    - ['CLASS', class name, unique_id, [list of superclass names], [attr1, value1], [attr2, value2], ..., [attrN, valueN]]
#   * anything else - ['INSTANCE', class name, unique_id, [attr1, value1], [attr2, value2], ..., [attrN, valueN]]
#
# the unique_id is derived from id(), which allows us to explicitly
# capture aliasing of compound values

import inspect

# Key: real ID from id()
# Value: a small integer for greater readability, set by cur_small_id
real_to_small_IDs = {}
cur_small_id = 1

# these variables will not be included into tracadata
ignored_names = ('__doc__', '__module__', '__return__', '__locals__', '__dict__', '__weakref__')
basic_types = {type(None): "NONETYPE", int: "INT", float: "FLOAT", bool: "BOOL", str: "STRING"}
container_types = {list: "LIST", tuple: "TUPLE", set: "SET", dict: "DICT"}

def encode(dat, ignore_id=False):
  """This function encodes the data dat into visualizable format. 
  Ignore_id indicates whether we need to assign id for dat."""
  def encode_helper(dat, compound_obj_ids):
    my_id = id(dat)

    global cur_small_id
    if my_id not in real_to_small_IDs:
      if ignore_id:
        real_to_small_IDs[my_id] = 99999
      else:
        real_to_small_IDs[my_id] = cur_small_id
      cur_small_id += 1

    if my_id in compound_obj_ids:
      return ['CIRCULAR_REF'.lower(), real_to_small_IDs[my_id]]

    new_compound_obj_ids = compound_obj_ids.union([my_id])
    my_small_id = real_to_small_IDs[my_id]

    typ = type(dat)
    if typ in basic_types:
      ret = [basic_types[typ].lower(), my_small_id, dat]
    
    elif typ in container_types:
      ret = [container_types[typ].lower(), my_small_id]
      if typ == dict:
          for (k, v) in dat.items():
              # don't display some built-in locals ...
              if k not in ignored_names:
                  ret.append([encode_helper(k, new_compound_obj_ids), encode_helper(v, new_compound_obj_ids)])
      else:
          for e in dat:
              ret.append(encode_helper(e, new_compound_obj_ids))
        
    elif inspect.isfunction(dat):
      function_name = dat.__code__.co_name + '('
      for var in inspect.getargspec(dat)[0]:
        function_name = function_name + var + ', '
      if function_name[-1] == ' ':
        function_name = function_name[:-2]
      function_name = function_name + ')' 
      ret = ['FUNCTION'.lower(), my_small_id, function_name]

    # akp: I chose to identify classes using inspect and instances by 
    # checking the type. I define an instance to be a value of any type not
    # handled in a special way above.
    # 
    # This may be controversial. Instances of classes are not well defined
    # in Python3, since classes are technically instances of the metaclass 
    # "type" (or another metaclass). Alternately, we could choose to 
    # identify (most) classes as those with the parent "type" 
    # (<class 'type'>), but that will fail if the metaclass is something 
    # other than "type".  
    elif inspect.isclass(dat):
      # TODO: Use "inspect.getclasstree" instead
      superclass_names = [e.__name__ for e in dat.__bases__]
      ret = ['CLASS'.lower(), dat.__name__, my_small_id, superclass_names]
      # To include a link to the class itself:
      #ret.append([encode_helper('__class__', new_compound_obj_ids), encode_helper(dat.__class__, new_compound_obj_ids)])

      # traverse inside of its __dict__ to grab attributes
      # (filter out useless-seeming ones):
      user_attrs = sorted([e for e in dat.__dict__.keys() if e not in ignored_names])
      for attr in user_attrs:
        ret.append([encode_helper(attr, new_compound_obj_ids), encode_helper(dat.__dict__[attr], new_compound_obj_ids)])

    # akp: I expect we will find new types in Python3 that will need to be handled
    # in special ways. 
    # TODO: check if setdescriptors and generators are handled correctly. inspect can help identify them.
    else:
      # TODO: It may be possible to use "inspect" to get the type name in a safer way.
      ret = ['INSTANCE'.lower(), dat.__class__.__name__, my_small_id]

      return ret

      # traverse inside of its __dict__ to grab attributes
      # (filter out useless-seeming ones):
      user_attrs = sorted([e for e in dat.__dict__.keys() if e not in ignored_names])
      for attr in user_attrs:
        ret.append([encode_helper(attr, new_compound_obj_ids), encode_helper(dat.__dict__[attr], new_compound_obj_ids)])

    return ret

  return encode_helper(dat, set())
