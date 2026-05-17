"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain import hub
from langchain.load import dumps

from utils import check_env_vars, print_section_header, save_yaml

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent.parent
PROMPT_KEY: str = "bug_to_user_story_v1"
PROMPT_PATH: Path = BASE_DIR / "prompts" / f"{PROMPT_KEY}.yml"


def _format_langchain_prompt(json_prompt: dict) -> dict:
    """Converte a estrutura do LangChain para YAML simplificado"""

    messages = json_prompt.get("kwargs", {}).get("messages", [])

    system_prompt = ""
    user_prompt = ""

    for message in messages:
        message_id = message.get("id", [])

        if "SystemMessagePromptTemplate" in message_id:
            system_prompt = (
                message.get("kwargs", {})
                .get("prompt", {})
                .get("kwargs", {})
                .get("template", "")
            )
        elif "HumanMessagePromptTemplate" in message_id:
            user_prompt = (
                message.get("kwargs", {})
                .get("prompt", {})
                .get("kwargs", {})
                .get("template", "")
            )

    return {
        PROMPT_KEY: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt.strip(),
            "user_prompt": user_prompt.strip(),
            "version": PROMPT_KEY.rsplit("_", maxsplit=1)[-1],
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }


def pull_prompts_from_langsmith() -> bool:
    """Pull prompts from LangSmith Hub."""

    print_section_header("Retornando prompts do LangSmith Hub")

    prompt_name = f"leonanluppi/{PROMPT_KEY}"
    output_file = str(PROMPT_PATH)

    try:
        print(f"Fazendo pull do prompt do LangSmith Hub: {prompt_name}")
        prompt = hub.pull(prompt_name)
        json_prompt = json.loads(dumps(prompt))
        print("   ✓ Prompt carregado com sucesso\n")

        print(f"Salvando prompt em prompts/{PROMPT_KEY}.yml")
        formatted_prompt = _format_langchain_prompt(json_prompt)
        save_yaml(formatted_prompt, output_file)
        print("   ✓ Prompt salvo com sucesso\n")

        return True
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False


def main():
    """Função principal"""

    if not check_env_vars(
        [
            "LANGSMITH_API_KEY",
            "LANGSMITH_ENDPOINT",
        ]
    ):
        return 1

    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
