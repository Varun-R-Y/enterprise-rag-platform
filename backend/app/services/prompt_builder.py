from app.schemas.document import RetrieveResult


class PromptBuilder:
    """
    Service to build well-structured prompts for the local Ollama Phi-3 Mini model
    using retrieved document chunks, conversation history, and the user's question.
    """

    MAX_HISTORY_TURNS = 5  # Cap history to last N exchanges to avoid token overflow

    def build_prompt(
        self,
        question: str,
        context: list[RetrieveResult],
        conversation_history: list[dict] | None = None,
    ) -> str:
        """
        Converts the user's question, context list, and conversation history
        into a single formatted prompt.

        Args:
            question: The user's question.
            context: List of RetrieveResult objects from semantic search.
            conversation_history: Optional list of {"role": str, "content": str} dicts
                                  representing prior conversation turns. Must be
                                  independent of any ORM models.

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
            "5. At the end of the answer, include a Sources section listing every document and page used.\n"
            "6. Use conversation history for continuity but always ground answers in the provided context."
        )

        # Build conversation history section
        history_str = ""
        if conversation_history:
            # Take only the last N turns to avoid token overflow
            trimmed = conversation_history[-(self.MAX_HISTORY_TURNS * 2):]
            history_parts = []
            for turn in trimmed:
                role = turn.get("role", "user").capitalize()
                content = turn.get("content", "")
                history_parts.append(f"{role}: {content}")
            history_str = "\n\n".join(history_parts)

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
        prompt = f"{system_instructions}\n\n"

        if history_str:
            prompt += (
                "========================================\n\n"
                "Conversation History\n\n"
                f"{history_str}\n\n"
            )

        prompt += (
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

