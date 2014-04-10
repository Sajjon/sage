r"""
Type A crystal on affine factorizations
"""
#*****************************************************************************
#  Copyright (C) 2014 Anne Schilling <anne at math.ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.structure.parent import Parent
from sage.structure.element_wrapper import ElementWrapper
from sage.structure.unique_representation import UniqueRepresentation
from sage.categories.classical_crystals import ClassicalCrystals
from sage.categories.enumerated_sets import EnumeratedSets
from sage.combinat.root_system.cartan_type import CartanType
from sage.combinat.root_system.weyl_group import WeylGroup

class AffineFactorizationCrystal(UniqueRepresentation, Parent):
    r"""
    This is an implementation of the crystal on affine factorizations
    with a cut-point, as introduced by Morse and Schilling,
    "Crystal operators and flag Gromov-Witten invariants".

    INPUT:

    - ``w`` -- an element in an (affine) Weyl group or a skew shape of `k`-bounded partitions (if `k` was specified)

    - ``n`` -- the number of factors in the factorization

    - ``x`` -- (default: ``None``) the cut point; if not specified it is determined as the minimal missing residue in ``w``

    - ``k`` -- (default: ``None``) positive integer, specifies that ``w`` is `k`-bounded or a `k+1`-core when specified

    EXAMPLES::

        sage: from sage.combinat.crystals.affine_factorization import AffineFactorizationCrystal
        sage: W = WeylGroup(['A',3,1], prefix='s')
        sage: w = W.from_reduced_word([2,3,2,1])
        sage: B = AffineFactorizationCrystal(w,3); B
        Crystal on affine factorizations of type A2 associated to s2*s3*s2*s1
        sage: B.list()
        [(1, s2, s3*s2*s1),
         (1, s3*s2, s3*s1),
         (1, s3*s2*s1, s3),
         (s3, s2, s3*s1),
         (s3, s2*s1, s3),
         (s3*s2, s1, s3),
         (s3*s2*s1, 1, s3),
         (s3*s2*s1, s3, 1),
         (s3*s2, 1, s3*s1),
         (s3*s2, s3, s1),
         (s3*s2, s3*s1, 1),
         (s2, 1, s3*s2*s1),
         (s2, s3, s2*s1),
         (s2, s3*s2, s1),
         (s2, s3*s2*s1, 1)]

    We can also access the crystal by specifying a skew shape in terms of `k`-bounded partitions::

        sage: AffineFactorizationCrystal([[3,1,1],[1]], 3, k=3)
        Crystal on affine factorizations of type A2 associated to s2*s3*s2*s1

    We can compute the highest weight elements::

        sage: hw = [w for w in B if w.is_highest_weight()]
        sage: hw
        [(1, s2, s3*s2*s1)]
        sage: hw[0].weight()
        (3, 1, 0)

    And show that this crystal is isomorphic to the tableau model of the same weight::

        sage: C = CrystalOfTableaux(['A',2],shape=[3,1])
        sage: GC = C.digraph()
        sage: GB = B.digraph()
        sage: GC.is_isomorphic(GB, edge_labels=True)
        True

    The crystal operators themselves move elements between adjacent factors::

        sage: b = hw[0];b
        (1, s2, s3*s2*s1)
        sage: b.f(1)
        (1, s3*s2, s3*s1)

    The cut point `x` is not supposed to occur in the reduced words for `w`::

        sage: B = AffineFactorizationCrystal([[3,2],[2]],4,x=0,k=3)
        Traceback (most recent call last):
        ...
        ValueError: x cannot be in reduced word of s0*s3*s2
    """
    @staticmethod
    def __classcall_private__(cls, w, n, x = None, k = None):
        r"""
        Classcall to mend the input.

        TESTS::

            sage: from sage.combinat.crystals.affine_factorization import AffineFactorizationCrystal
            sage: A = AffineFactorizationCrystal([[3,1],[1]], 4, k=3); A
            Crystal on affine factorizations of type A3 associated to s3*s2*s1
            sage: AC = AffineFactorizationCrystal([Core([4,1],4),Core([1],4)], 4, k=3)
            sage: AC is A
            True
        """
        if k is not None:
            from sage.combinat.core import Core
            from sage.combinat.partition import Partition
            W = WeylGroup(['A',k,1], prefix='s')
            if isinstance(w[0], Core):
                w = [w[0].to_bounded_partition(), w[1].to_bounded_partition()]
            else:
                w = [Partition(w[0]), Partition(w[1])]
            w0 = W.from_reduced_word(w[0].from_kbounded_to_reduced_word(k))
            w1 = W.from_reduced_word(w[1].from_kbounded_to_reduced_word(k))
            w = w0*(w1.inverse())
        return super(AffineFactorizationCrystal, cls).__classcall__(cls, w, n, x)

    def __init__(self, w, n, x = None):
        r"""
        EXAMPLES::

            sage: from sage.combinat.crystals.affine_factorization import AffineFactorizationCrystal
            sage: B = AffineFactorizationCrystal([[3,2],[2]],4,x=0,k=3)
            Traceback (most recent call last):
            ...
            ValueError: x cannot be in reduced word of s0*s3*s2

            sage: B = AffineFactorizationCrystal([[3,2],[2]],4,k=3)
            sage: B.x
            1
            sage: B.w
            s0*s3*s2
            sage: B.k
            3
            sage: B.n
            4

        TESTS::

            sage: from sage.combinat.crystals.affine_factorization import AffineFactorizationCrystal
            sage: W = WeylGroup(['A',3,1], prefix='s')
            sage: w = W.from_reduced_word([2,3,2,1])
            sage: B = AffineFactorizationCrystal(w,3)
            sage: TestSuite(B).run()
        """
        Parent.__init__(self, category = ClassicalCrystals())
        self.n = n
        self.k = w.parent().n-1
        self.w = w
        cartan_type = CartanType(['A',n-1])
        self._cartan_type = cartan_type
        from sage.combinat.sf.sf import SymmetricFunctions
        from sage.rings.all import QQ
        Sym = SymmetricFunctions(QQ)
        s = Sym.schur()
        support = s(w.stanley_symmetric_function()).support()
        support = [ [0]*(n-len(mu))+[mu[len(mu)-i-1] for i in range(len(mu))] for mu in support]
        generators = [tuple(p) for mu in support for p in affine_factorizations(w,n,mu)]
        #generators = [tuple(p) for p in affine_factorizations(w, n)]
        self.module_generators = [self(t) for t in generators]
        if x is None:
            if generators != []:
                x = min( set(range(self.k+1)).difference(set(
                            sum([i.reduced_word() for i in generators[0]],[]))))
            else:
                x = 0
        if x in set(w.reduced_word()):
            raise ValueError("x cannot be in reduced word of {}".format(w))
        self.x = x

    def _repr_(self):
        r"""
        EXAMPLES::

            sage: from sage.combinat.crystals.affine_factorization import AffineFactorizationCrystal
            sage: W = WeylGroup(['A',3,1], prefix='s')
            sage: w = W.from_reduced_word([3,2,1])
            sage: AffineFactorizationCrystal(w,4)
            Crystal on affine factorizations of type A3 associated to s3*s2*s1

            sage: AffineFactorizationCrystal([[3,1],[1]], 4, k=3)
            Crystal on affine factorizations of type A3 associated to s3*s2*s1
        """
        return "Crystal on affine factorizations of type A{} associated to {}".format(self.n-1, self.w)

    # temporary workaround while an_element is overriden by Parent
    _an_element_ = EnumeratedSets.ParentMethods._an_element_

    class Element(ElementWrapper):

        def e(self, i):
            r"""
            Return the action of `e_i` on ``self``.

            EXAMPLES::

                sage: from sage.combinat.crystals.affine_factorization import AffineFactorizationCrystal
                sage: B = AffineFactorizationCrystal([[3,1],[1]], 4, k=3)
                sage: W = B.w.parent()
                sage: t = B((W.one(),W.one(),W.from_reduced_word([3]),W.from_reduced_word([2,1]))); t
                (1, 1, s3, s2*s1)
                sage: t.e(1)
                (1, 1, 1, s3*s2*s1)
            """
            if i not in self.index_set():
                raise ValueError("i must be in the index set")
            b = self.bracketing(i)
            if not b[0]:
                return None
            W = self.parent().w.parent()
            x = self.parent().x
            k = self.parent().k
            n = self.parent().n
            a = min(b[0])
            left = [j for j in (self.value[n-i-1]).reduced_word() if j != (a+x)%(k+1)]
            right = [(j-x)%(k+1) for j in (self.value[n-i]).reduced_word()]
            m = max([j for j in range(a) if (j+x)%(k+1) not in left])
            right += [m+1]
            right.sort(reverse=True)
            right = [(j+x)%(k+1) for j in right]
            t = [self.value[j] for j in range(n-i-1)] + [W.from_reduced_word(left)] + [W.from_reduced_word(right)] + [self.value[j] for j in range(n-i+1,n)]
            return self.parent()(tuple(t))

        def f(self, i):
            r"""
            Return the action of `f_i` on ``self``.

            EXAMPLES::

                sage: from sage.combinat.crystals.affine_factorization import AffineFactorizationCrystal
                sage: B = AffineFactorizationCrystal([[3,1],[1]], 4, k=3)
                sage: W = B.w.parent()
                sage: t = B((W.one(),W.one(),W.from_reduced_word([3]),W.from_reduced_word([2,1]))); t
                (1, 1, s3, s2*s1)
                sage: t.f(2)
                (1, s3, 1, s2*s1)
                sage: t.f(1)
                (1, 1, s3*s2, s1)
            """
            if i not in self.index_set():
                raise ValueError("i must be in the index set")
            b = self.bracketing(i)
            if not b[1]:
                return None
            W = self.parent().w.parent()
            x = self.parent().x
            k = self.parent().k
            n = self.parent().n
            a = max(b[1])
            right = [j for j in (self.value[n-i]).reduced_word() if j != (a+x)%(k+1)]
            left = [(j-x)%(k+1) for j in (self.value[n-i-1]).reduced_word()]
            m = min([j for j in range(a+1,k+2) if (j+x)%(k+1) not in right])
            left += [m-1]
            left.sort(reverse=True)
            left = [(j+x)%(k+1) for j in left]
            t = [self.value[j] for j in range(n-i-1)] + [W.from_reduced_word(left)] + [W.from_reduced_word(right)] + [self.value[j] for j in range(n-i+1,n)]
            return self.parent()(tuple(t))

        def bracketing(self, i):
            r"""
            Removes all bracketed letters between `i`-th and `i+1`-th entry.

            EXAMPLES::

                sage: from sage.combinat.crystals.affine_factorization import AffineFactorizationCrystal
                sage: B = AffineFactorizationCrystal([[3,1],[1]], 3, k=3, x=4)
                sage: W = B.w.parent()
                sage: t = B((W.one(),W.from_reduced_word([3]),W.from_reduced_word([2,1]))); t
                (1, s3, s2*s1)
                sage: t.bracketing(1)
                [[3], [2, 1]]
            """
            n = self.parent().n
            x = self.parent().x
            k = self.parent().k
            right = (self.value[n-i]).reduced_word()
            left = (self.value[n-i-1]).reduced_word()
            right_n = [(j-x)%(k+1) for j in right]
            left_n = [(j-x)%(k+1) for j in left]
            left_unbracketed = []
            while left_n:
                m = max(left_n)
                left_n.remove(m)
                l = [j for j in right_n if j>m]
                if l:
                    right_n.remove(min(l))
                else:
                    left_unbracketed += [m]
            return [[j for j in left_unbracketed],[j for j in right_n]]


def affine_factorizations(w, l, weight=None):
    r"""
    Return all factorizations of ``w`` into ``l`` factors or of weight ``weight``.

    INPUT:

    - ``w`` -- an (affine) permutation or element of the (affine) Weyl group

    - ``l`` -- nonegative integer

    - ``weight`` -- (default: None) tuple of nonnegative integers specifying the length of the factors

    EXAMPLES::

       sage: W = WeylGroup(['A',3,1], prefix='s')
       sage: w = W.from_reduced_word([3,2,3,1,0,1])
       sage: from sage.combinat.crystals.affine_factorization import affine_factorizations
       sage: affine_factorizations(w,4)
       [[s2, s3, s0, s2*s1*s0],
       [s2, s3, s2*s0, s1*s0],
       [s2, s3, s2*s1*s0, s1],
       [s2, s3*s2, s0, s1*s0],
       [s2, s3*s2, s1*s0, s1],
       [s2, s3*s2*s1, s0, s1],
       [s3*s2, s3, s0, s1*s0],
       [s3*s2, s3, s1*s0, s1],
       [s3*s2, s3*s1, s0, s1],
       [s3*s2*s1, s3, s0, s1]]

       sage: W = WeylGroup(['A',2], prefix='s')
       sage: w0 = W.long_element()
       sage: affine_factorizations(w0,3)
       [[1, s1, s2*s1],
       [1, s2*s1, s2],
       [s1, 1, s2*s1],
       [s1, s2, s1],
       [s1, s2*s1, 1],
       [s2, s1, s2],
       [s2*s1, 1, s2],
       [s2*s1, s2, 1]]
       sage: affine_factorizations(w0,3,(0,1,2))
       [[1, s1, s2*s1]]
       sage: affine_factorizations(w0,3,(1,1,1))
       [[s1, s2, s1], [s2, s1, s2]]
       sage: W = WeylGroup(['A',3], prefix='s')
       sage: w0 = W.long_element()
       sage: affine_factorizations(w0,6,(1,1,1,1,1,1))
       [[s1, s2, s1, s3, s2, s1],
       [s1, s2, s3, s1, s2, s1],
       [s1, s2, s3, s2, s1, s2],
       [s1, s3, s2, s1, s3, s2],
       [s1, s3, s2, s3, s1, s2],
       [s2, s1, s2, s3, s2, s1],
       [s2, s1, s3, s2, s1, s3],
       [s2, s1, s3, s2, s3, s1],
       [s2, s3, s1, s2, s1, s3],
       [s2, s3, s1, s2, s3, s1],
       [s2, s3, s2, s1, s2, s3],
       [s3, s1, s2, s1, s3, s2],
       [s3, s1, s2, s3, s1, s2],
       [s3, s2, s1, s2, s3, s2],
       [s3, s2, s1, s3, s2, s3],
       [s3, s2, s3, s1, s2, s3]]
       sage: affine_factorizations(w0,6,(0,0,0,1,2,3))
       [[1, 1, 1, s1, s2*s1, s3*s2*s1]]
    """
    if weight is None:
        if l==0:
            if w.is_one():
                return [[]]
            else:
                return []
        else:
            return [[u]+p for (u,v) in w.left_pieri_factorizations() for p in affine_factorizations(v,l-1) ]
    else:
        if l != len(weight):
            return []
        if l==0:
            if w.is_one():
                return [[]]
            else:
                return []
        else:
            return [[u]+p for (u,v) in w.left_pieri_factorizations(max_length=weight[0]) if u.length() == weight[0]
                    for p in affine_factorizations(v,l-1,weight[1:]) ]
