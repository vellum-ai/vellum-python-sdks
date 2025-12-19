from vellum.workflows.references.array import ArrayReference
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.references.dictionary import DictionaryReference
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    pass


class TestArrayReference:
    def test_array_reference__resolve_with_constant_items(self):
        """
        Tests that ArrayReference resolves constant items correctly.
        """
        # GIVEN an array reference with constant items
        array_ref = ArrayReference([1, 2, 3])

        # AND a state to resolve against
        state = TestState()

        # WHEN we resolve the array reference
        result = array_ref.resolve(state)

        # THEN we get the expected list
        assert result == [1, 2, 3]

    def test_array_reference__resolve_with_nested_descriptors(self):
        """
        Tests that ArrayReference resolves nested descriptors correctly.
        """
        # GIVEN an array reference with nested ConstantValueReference descriptors
        nested_ref = ConstantValueReference("nested_value")
        array_ref = ArrayReference([nested_ref, "constant"])

        # AND a state to resolve against
        state = TestState()

        # WHEN we resolve the array reference
        result = array_ref.resolve(state)

        # THEN we get the expected list with resolved values
        assert result == ["nested_value", "constant"]

    def test_array_reference__resolve_with_mixed_items(self):
        """
        Tests that ArrayReference resolves mixed constant and descriptor items correctly.
        """
        # GIVEN an array reference with mixed items
        nested_ref1 = ConstantValueReference(10)
        nested_ref2 = ConstantValueReference(20)
        array_ref = ArrayReference([nested_ref1, 15, nested_ref2])

        # AND a state to resolve against
        state = TestState()

        # WHEN we resolve the array reference
        result = array_ref.resolve(state)

        # THEN we get the expected list with resolved values
        assert result == [10, 15, 20]


class TestDictionaryReference:
    def test_dictionary_reference__resolve_with_constant_values(self):
        """
        Tests that DictionaryReference resolves constant values correctly.
        """
        # GIVEN a dictionary reference with constant values
        dict_ref = DictionaryReference({"key1": "value1", "key2": "value2"})

        # AND a state to resolve against
        state = TestState()

        # WHEN we resolve the dictionary reference
        result = dict_ref.resolve(state)

        # THEN we get the expected dictionary
        assert result == {"key1": "value1", "key2": "value2"}

    def test_dictionary_reference__resolve_with_nested_descriptors(self):
        """
        Tests that DictionaryReference resolves nested descriptors correctly.
        """
        # GIVEN a dictionary reference with nested ConstantValueReference descriptors
        nested_ref = ConstantValueReference("nested_value")
        dict_ref = DictionaryReference({"key1": nested_ref, "key2": "constant"})

        # AND a state to resolve against
        state = TestState()

        # WHEN we resolve the dictionary reference
        result = dict_ref.resolve(state)

        # THEN we get the expected dictionary with resolved values
        assert result == {"key1": "nested_value", "key2": "constant"}

    def test_dictionary_reference__resolve_with_mixed_values(self):
        """
        Tests that DictionaryReference resolves mixed constant and descriptor values correctly.
        """
        # GIVEN a dictionary reference with mixed values
        nested_ref1 = ConstantValueReference(10)
        nested_ref2 = ConstantValueReference(20)
        dict_ref = DictionaryReference({"a": nested_ref1, "b": 15, "c": nested_ref2})

        # AND a state to resolve against
        state = TestState()

        # WHEN we resolve the dictionary reference
        result = dict_ref.resolve(state)

        # THEN we get the expected dictionary with resolved values
        assert result == {"a": 10, "b": 15, "c": 20}
