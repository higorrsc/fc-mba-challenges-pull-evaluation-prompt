"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain import hub
from langchain.prompts import ChatPromptTemplate

from utils import (
    check_env_vars,
    load_yaml,
    print_section_header,
    validate_prompt_structure,
)

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent.parent
PROMPT_KEY: str = "bug_to_user_story_v2"
PROMPT_PATH: Path = BASE_DIR / "prompts" / f"{PROMPT_KEY}.yml"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """

    try:
        print("Criando prompt para o LangSmith Hub...")
        prompt_messages = [
            ("system", prompt_data["system_prompt"]),
            ("user", prompt_data["user_prompt"] or prompt_data["{bug_report}"]),
        ]
        prompt_template = ChatPromptTemplate.from_messages(prompt_messages)

        prompt_tags = prompt_data.get("tags", []) + prompt_data.get(
            "techniques_applied", []
        )
        prompt_description = prompt_data.get("description", "")
        username = os.getenv("USERNAME_LANGSMITH_HUB")
        full_repo_name = f"{username}/{prompt_name}"

        print(f"Enviando prompt {full_repo_name} para o LangSmith Hub...")
        prompt_url = hub.push(
            repo_full_name=full_repo_name,
            object=prompt_template,
            new_repo_is_public=True,
            new_repo_description=prompt_description,
            tags=prompt_tags,
        )
        print(f"Prompt {prompt_name} enviado com sucesso para o LangSmith Hub!")
        print(f"URL: {prompt_url}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """

    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""

    print_section_header("Push prompt to LangSmith Hub")

    if not check_env_vars(
        [
            "LANGSMITH_API_KEY",
            "LANGSMITH_ENDPOINT",
            "USERNAME_LANGSMITH_HUB",
        ]
    ):
        return 1

    if not PROMPT_PATH.exists():
        print(
            f"❌ Arquivo de prompt não encontrado: {PROMPT_PATH.parent.name}/{PROMPT_PATH.name}"
        )
        print("\nCertifique-se de que o arquivo existe antes de continuar.")
        return 1

    prompt_data = load_yaml(str(PROMPT_PATH))
    prompt = prompt_data.get(PROMPT_KEY, None)  # type:ignore

    if not prompt:
        print(
            f"❌ Prompt '{PROMPT_KEY}' não encontrado "
            f"no arquivo {PROMPT_PATH.parent.name}/{PROMPT_PATH.name}"
        )
        return 1

    prompt_is_valid, prompt_errors = validate_prompt(prompt)
    if not prompt_is_valid:
        print("❌ Prompt inválido")
        for error in prompt_errors:
            print(f"   - {error}")
        return 1

    return 0 if push_prompt_to_langsmith(PROMPT_KEY, prompt) else 1


if __name__ == "__main__":
    sys.exit(main())
