# Python imports
from collections import defaultdict

# UFL imports
from output import ufl_assert, ufl_error

#--- Indexing ---

class Index:
    __slots__ = ("_name", "_count")
    
    _globalcount = 0
    def __init__(self, name = None, count = None):
        self._name = name
        if count is None:
            self._count = Index._globalcount
            Index._globalcount += 1
        else:
            self._count = count
            if count >= Index._globalcount:
                Index._globalcount = count + 1
    
    def free_indices(self):
        ufl_error("Why would you want to get the free indices of an Index? Please explain at ufl-dev@fenics.org...")
    
    def rank(self):
        ufl_error("Why would you want to get the rank of an Index? Please explain at ufl-dev@fenics.org...")
    
    def __str__(self):
        return "i_%d" % self._count # TODO: use name? Maybe just remove name, adds possible confusion of what ID's an Index (which is the count alone).
    
    def __repr__(self):
        return "Index(%s, %d)" % (repr(self._name), self._count)

class FixedIndex:
    __slots__ = ("_value",)
    
    def __init__(self, value):
        ufl_assert(isinstance(value, int), "Expecting integer value for fixed index.")
        self._value = value
    
    def free_indices(self):
        ufl_error("Why would you want to get the free indices of an Index? Please explain at ufl-dev@fenics.org...")
    
    def rank(self):
        ufl_error("Why would you want to get the rank of an Index? Please explain at ufl-dev@fenics.org...")
    
    def __str__(self):
        return "%d" % self._value
    
    def __repr__(self):
        return "FixedIndex(%d)" % self._value

class AxisType:
    __slots__ = () #("value",)
    
    def __init__(self):
        pass
    
    def free_indices(self):
        ufl_error("Why would you want to get the free indices of an Axis? Please explain at ufl-dev@fenics.org...")
    
    def rank(self):
        ufl_error("Why would you want to get the rank of an Axis? Please explain at ufl-dev@fenics.org...")
    
    def __str__(self):
        return ":"
    
    def __repr__(self):
        return "Axis"

# only need one of these, like None, Ellipsis etc., can use "a is Axis" or "isinstance(a, AxisType)"
Axis = AxisType()

def as_index(i):
    """Takes something the user might input as part of an index tuple, and returns an actual UFL index object."""
    if isinstance(i, (Index, FixedIndex)):
        return i
    elif isinstance(i, int):
        return FixedIndex(i)
    elif isinstance(i, slice):
        ufl_assert((i.start is None) and (i.stop is None) and (i.step is None), "Partial slices not implemented, only [:]")
        return Axis
    else:
        ufl_error("Can convert this object to index: %s" % repr(i))


def as_index_tuple(indices, rank):
    """Takes something the user might input as an index tuple inside [], and returns a tuple of actual UFL index objects.
    
    These types are supported:
    - Index
    - int => FixedIndex
    - Complete slice (:) => Axis
    - Ellipsis (...) => multiple Axis
    """
    if not isinstance(indices, tuple):
        indices = (indices,)
    pre  = []
    post = []
    found = False
    for j, idx in enumerate(indices):
        if found:
            if idx is Ellipsis:
                found = True
            else:
                pre.append(as_index(idx))
        else:
            ufl_assert(not idx is Ellipsis, "Found duplicate ellipsis.")
            post.append(as_index(idx))
    
    # replace ellipsis with a number of Axis objects
    indices = pre + [Axis]*(rank-len(pre)-len(post)) + post
    return tuple(indices)


def extract_indices(indices):
    ufl_assert(isinstance(indices, tuple), "Expecting index tuple.")
    ufl_assert(all(isinstance(i, (Index, FixedIndex, AxisType)) for i in indices), "Expecting proper UFL objects.")

    fixed_indices = [(i,idx) for i,idx in enumerate(indices) if isinstance(idx, FixedIndex)]
    num_unassigned_indices = sum(1 for i in indices if i is Axis)

    index_count = defaultdict(int)
    for i in indices:
        if isinstance(i, Index):
            index_count[i] += 1
    
    unique_indices = index_count.keys()
    handled = set()

    ufl_assert(all(i <= 2 for i in index_count.values()), "Too many index repetitions in %s" % repr(indices))
    free_indices     = [i for i in unique_indices if index_count[i] == 1]
    repeated_indices = [i for i in unique_indices if index_count[i] == 2]

    # use tuples for consistency
    fixed_indices    = tuple(fixed_indices)
    free_indices     = tuple(free_indices)
    repeated_indices = tuple(repeated_indices)
    
    ufl_assert(len(fixed_indices) + len(free_indices) + 2*len(repeated_indices) + num_unassigned_indices == len(indices), "Logic breach in extract_indices.")
    
    return (fixed_indices, free_indices, repeated_indices, num_unassigned_indices)

class MultiIndex:
    __slots__ = ("_indices",)
    
    def __init__(self, indices, rank):
        self._indices = as_index_tuple(indices, rank)
    
    def operands(self):
        return self._indices
    
    def free_indices(self):
        ufl_error("Why would you want to get the free indices of a MultiIndex? Please explain at ufl-dev@fenics.org...")
    
    def rank(self):
        ufl_error("Why would you want to get the rank of a MultiIndex? Please explain at ufl-dev@fenics.org...")
    
    def __str__(self):
        return ", ".join(str(i) for i in self._indices)
    
    def __repr__(self):
        return "MultiIndex(%s, %d)" % (repr(self._indices), len(self._indices))

    def __len__(self):
        return len(self._indices)