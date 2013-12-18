"""A full binary tree example"""

from dbcbet.dbcbet import pre, post, inv, bet, finitize, finitize_method
from dbcbet.helpers import state, argument_types

def full_tree_invariant(self):
    return self._leaf() or self._full()

def is_full(self):
    return self._full()

def is_leaf(self):
    return self._leaf()

@inv(full_tree_invariant)
class FullBinaryTree(object):
    @finitize_method([1,2,3,4])
    def __init__(self, value):
        self.value = value
        self.left_subtree = None
        self.right_subtree = None

    def leaf(self):
        return self._leaf()

    def _leaf(self):
        return self.left_subtree is None and self.right_subtree is None

    def full(self):
        return self._full()

    def _full(self):
        return self.left_subtree is not None and self.right_subtree is not None

    def nodes(self):
        return 1 if self.leaf() else self.left_subtree.nodes() + self.right_subtree.nodes()

    @pre(argument_types("examples.FullBinaryTree"))
    def add_left_subtree(self, left_subtree):
        self.left_subtree = left_subtree

    @pre(argument_types("examples.FullBinaryTree"))
    def add_right_subtree(self, right_subtree):
        self.right_subtree = right_subtree

    @pre(argument_types("examples.FullBinaryTree", "examples.FullBinaryTree"))
    @pre(state(is_leaf))
    @post(state(is_full))
    def add_subtrees(self, left, right):
        self.left_subtree = left
        self.right_subtree = right
        
    @pre(state(is_full))
    @pre(argument_types("examples.FullBinaryTree"))
    def replace_left_subtree(self, left_subtree):
        self.left_subtree = left_subtree

    @pre(state(is_full))    
    @pre(argument_types("examples.FullBinaryTree"))
    def replace_right_subtree(self, right_subtree):
        self.right_subtree = right_subtree

    def __str__(self):
        return self._s("")

    def __hash__(self):
        return hash((self.value, self.left_subtree, self.right_subtree))

    def __eq__(self, other):
        partial = True
        if self.left_subtree is not None and other.left_subtree is not None:
            partial = partial and (self.left_subtree == other.left_subtree)
        else:
            partial = partial and self.left_subtree is None and other.left_subtree is None
        if self.right_subtree is not None and other.right_subtree is not None:
            partial = partial and (self.right_subtree == other.right_subtree)
        else:
            partial = partial and self.right_subtree is None and other.right_subtree is None
        partial = partial and (self.value == other.value)
        return partial

    def _s(self, pad):
        ret = ""
        ret += "\n"+pad
        ret += "  value: " + self.value
        ret += "  # nodes: " + self.nodes()
        if self.left_subtree:
            ret += '\n' + pad
            ret += "  left subtree: " + self.left_subtree._s(pad + "  ")
            assert self.right_subtree
            ret += '\n' + pad
            ret += "  right subtree: " + self.right_subtree._s(pad + "  ")
        ret += "\n"
        return ret

if __name__ == "__main__":
    bet(FullBinaryTree).run()

# java testcases
# FullBinaryTree<Integer> tree1 = new FullBinaryTree<>( 1 );
# FullBinaryTree<Integer> tree2 = new FullBinaryTree<>( 2 );
# FullBinaryTree<Integer> tree3 = new FullBinaryTree<>( 3 );
# FullBinaryTree<Integer> tree4 = new FullBinaryTree<>( 4 );
# tree2.addSubtrees(  tree1, tree1 );
# tree3.addSubtrees( tree2, tree1 );
# tree4.addSubtrees( tree1, tree2 );
# System.out.println( "tree1: " + tree1 );
# System.out.println( "tree2: " + tree2 );
# System.out.println( "tree3: " + tree3 );
# System.out.println( "tree4: " + tree4 );
