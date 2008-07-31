""" Test whether HasTraits objects with cycles can be garbage collected.
"""

# Standard library imports
import gc
import time
import unittest

# Enthought library imports
from enthought.traits.api import HasTraits, Any

class TestCase(unittest.TestCase):
    def _simple_cycle_helper(self, foo_class):
        """ Can the garbage collector clean up a cycle with traits objects?
        """

        # Create two Foo objects that refer to each other.
        first = foo_class()
        second = foo_class(child=first)
        first.child=second

        # get their ids
        foo_ids =  [id(first), id(second)]

        # delete the items so that they can be garbage collected
        del first, second

        # tell the garbage collector to pick up the litter.
        gc.collect()

        # Now grab all objects in the process and ask for their ids
        all_ids = [id(obj) for obj in gc.get_objects()]

        # Ensure that neither of the Foo object ids are in this list
        for foo_id in foo_ids:
            self.assertTrue(foo_id not in all_ids)

    def test_simple_cycle_oldstyle_class(self):
        """ Can the garbage collector clean up a cycle with old style class?
        """
        class Foo:
            def __init__(self,child=None):
                self.child = child

        self._simple_cycle_helper(Foo)

    def test_simple_cycle_newstyle_class(self):
        """ Can the garbage collector clean up a cycle with new style class?
        """
        class Foo(object):
            def __init__(self,child=None):
                self.child = child

        self._simple_cycle_helper(Foo)

    def test_simple_cycle_hastraits(self):
        """ Can the garbage collector clean up a cycle with traits objects?
        """
        class Foo(HasTraits):
            child = Any

        self._simple_cycle_helper(Foo)

    def test_reference_to_trait_dict(self):
        """ Does a HasTraits object refer to its __dict__ object?

            This test may point to why the previous one fails.  Even if it
            doesn't, the functionality is needed for detecting problems
            with memory in debug.memory_tracker
        """

        class Foo(HasTraits):
            child = Any

        foo = Foo()

        # It seems like foo sometimes has not finished construction yet, so the
        # frame found by referrers is not _exactly_ the same as Foo(). For more
        # information, see the gc doc: http://docs.python.org/lib/module-gc.html
        #
        # The documentation says that this (get_referrers) should be used for no
        # purpose other than debugging, so this is really not a good way to test
        # the code.

        time.sleep(0.1)
        referrers = gc.get_referrers(foo.__dict__)

        self.assertTrue(len(referrers) > 0)
        self.assertTrue(foo in referrers)

if __name__ == '__main__':
    unittest.main()
