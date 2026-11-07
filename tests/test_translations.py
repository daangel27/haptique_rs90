"""Keep localized service descriptions compatible with their placeholders."""

import json
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("service", "field", "entity_id"),
    [
        ("trigger_macro", "rs90_macro_id", "switch.macro_movie"),
        ("trigger_device_command", "rs90_device_id", "sensor.commands_movie"),
    ],
)
def test_french_service_descriptions_accept_name(service, field, entity_id):
    translations = json.loads(
        (
            Path(__file__).parents[1]
            / "custom_components/haptique_rs90/translations/fr.json"
        ).read_text(encoding="utf-8")
    )
    description = translations["services"][service]["fields"][field]["description"]

    assert entity_id in description.format(name="movie")
