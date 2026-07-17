from app.schemas.document import RetrieveResult


class PromptBuilder:
    """
    Service to build well-structured prompts for the local Ollama Phi-3 Mini model
    using retrieved document chunks and the user's question.
    """

    def build_prompt(self, question: str, context: list[RetrieveResult]) -> str:
        """
        Converts the user's question and context list into a single formatted prompt.

        Args:
            question: The user's question.
            context: List of RetrieveResult objects from semantic search.

        Returns:
            The structured prompt string.
        """
        system_instructions = (
            "Prompt Version: 1.0\n\n"
            "You are an Enterprise Knowledge Assistant.\n\n"
            "You answer questions ONLY using the supplied document context.\n\n"
            "Rules:\n\n"
            "1. Use ONLY the provided context.\n"
            "2. Never use outside knowledge.\n"
            "3. If the answer is not explicitly supported by the provided context, do not infer or guess.\n"
            "   Reply exactly:\n\n"
            '   "I could not find that information in the provided documents."\n\n'
            "4. Keep answers concise and professional.\n"
            "5. At the end of the answer, include a Sources section listing every document and page used."
        )

        context_parts = []
        for item in context:
            part = (
                f"Document: {item.original_filename}\n"
                f"Page: {item.page}\n\n"
                f"Content:\n{item.text}"
            )
            context_parts.append(part)

        # Separate each document with the horizontal separator
        separator = "\n\n----------------------------------------\n\n"
        context_str = separator.join(context_parts)

        # Build the final prompt
        prompt = (
            f"{system_instructions}\n\n"
            "========================================\n\n"
            "Context\n\n"
            f"{context_str}\n\n"
            "========================================\n\n"
            "Question\n\n"
            f"{question}\n\n"
            "========================================\n\n"
            "Answer:\n"
        )
        return prompt
