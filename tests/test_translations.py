"""Service descriptions must not contain ICU placeholders.

Home Assistant's frontend formats service texts as ICU messages without
supplying any values, so a literal ``{name}`` raises MISSING_VALUE when the
action is opened in Developer tools / the automation editor.
"""

import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1] / "custom_components/haptique_rs90"
PLACEHOLDER = re.compile(r"\{[^}]*\}")


def _service_texts(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from _service_texts(value)
    elif isinstance(node, str):
        yield node


@pytest.mark.parametrize(
    "path", ["strings.json", "translations/en.json", "translations/fr.json"]
)
def test_service_texts_have_no_placeholders(path):
    services = json.loads((ROOT / path).read_text(encoding="utf-8"))["services"]
    offending = [text for text in _service_texts(services) if PLACEHOLDER.search(text)]
    assert offending == []


@pytest.mark.parametrize("path", ["services.yaml", "services.fr.yaml"])
def test_service_yaml_has_no_placeholders(path):
    services = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    offending = [text for text in _service_texts(services) if PLACEHOLDER.search(text)]
    assert offending == []
