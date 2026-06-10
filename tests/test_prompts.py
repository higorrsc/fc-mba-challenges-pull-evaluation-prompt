"""
Testes automatizados para validação de prompts.
"""

import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


BASE_DIR: Path = Path(__file__).resolve().parent.parent
PROMPT_KEY: str = "bug_to_user_story_v2"
PROMPT_PATH: Path = BASE_DIR / "prompts" / f"{PROMPT_KEY}.yml"


def load_prompts(file_path: str) -> Any:
    """Carrega prompts do arquivo YAML."""

    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(name="prompt_data")
def prompt_data_fixture() -> dict[str, Any]:
    """Retorna dados do prompt."""

    data = load_prompts(str(PROMPT_PATH)) or {}
    return data.get(PROMPT_KEY, {})


@pytest.fixture(name="system_prompt")
def system_prompt_fixture(prompt_data) -> str:
    """Retorna o system_prompt do prompt"""

    return prompt_data.get("system_prompt", "").lower()


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""

        assert "system_prompt" in prompt_data
        assert prompt_data["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self, system_prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""

        roles = [
            "você é",
            "atue como",
            "aja como",
            "você será",
            "you are",
            "you will be",
            "act as",
        ]
        assert any(role in system_prompt for role in roles)

    def test_prompt_mentions_format(self, system_prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""

        expected_formats = [
            "markdown",
            "user story",
            "como um",
            "as a",
            "given",
            "when",
            "then",
        ]

        assert any(fmt in system_prompt for fmt in expected_formats)

    def test_prompt_has_few_shot_examples(self, system_prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""

        example_indicators = [
            "exemplo",
            "example",
            "entrada",
            "input",
            "output",
            "saída",
        ]

        assert any(indicator in system_prompt for indicator in example_indicators)

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""

        full_text = str(prompt_data).lower()
        assert "[todo]" not in full_text
        assert "todo:" not in full_text

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""

        techniques = prompt_data.get("techniques_applied", {})

        assert isinstance(techniques, list)
        assert len(techniques) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
