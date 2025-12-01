"""Tests for trigger metadata utility functions."""

from unittest.mock import patch
import uuid

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.utils.uuids import get_trigger_attribute_id


class TestTrigger(IntegrationTrigger):
    """Test trigger with attributes for testing metadata lookup."""

    value: str
    other: str

    class Config(IntegrationTrigger.Config):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "test"
        slug = "test"


def test_trigger_attribute_reference_id__uses_metadata_when_available():
    """
    Tests that TriggerAttributeReference.id returns the ID from metadata.json
    when available, rather than generating a hash-based ID.
    """
    # GIVEN a trigger attribute reference
    reference = TestTrigger.value
    assert isinstance(reference, TriggerAttributeReference)

    # AND a metadata ID that differs from the hash-based ID
    metadata_id = uuid.uuid4()
    hash_based_id = get_trigger_attribute_id(TestTrigger, "value")
    assert metadata_id != hash_based_id

    # WHEN we mock the metadata lookup to return our metadata ID
    with patch(
        "vellum.workflows.references.trigger.get_trigger_attribute_id_from_metadata",
        return_value=metadata_id,
    ):
        # THEN the reference.id should return the metadata ID
        assert reference.id == metadata_id


def test_trigger_attribute_reference_id__falls_back_to_hash_when_no_metadata():
    """
    Tests that TriggerAttributeReference.id falls back to hash-based ID
    when metadata.json is not available.
    """
    # GIVEN a trigger attribute reference
    reference = TestTrigger.value
    assert isinstance(reference, TriggerAttributeReference)

    # AND the expected hash-based ID
    expected_hash_id = get_trigger_attribute_id(TestTrigger, "value")

    # WHEN metadata lookup returns None (no metadata available)
    with patch(
        "vellum.workflows.references.trigger.get_trigger_attribute_id_from_metadata",
        return_value=None,
    ):
        # THEN the reference.id should return the hash-based ID
        assert reference.id == expected_hash_id


def test_trigger_attribute_reference_id__different_attributes_get_different_ids():
    """
    Tests that different attributes on the same trigger get different IDs.
    """
    # GIVEN two different attribute references on the same trigger
    value_ref = TestTrigger.value
    other_ref = TestTrigger.other

    # WHEN we get their IDs (without metadata)
    with patch(
        "vellum.workflows.references.trigger.get_trigger_attribute_id_from_metadata",
        return_value=None,
    ):
        value_id = value_ref.id
        other_id = other_ref.id

    # THEN they should have different IDs
    assert value_id != other_id
