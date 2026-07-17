from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """
    Abstract base class for all Large Language Model services.
    """

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """
        Asynchronously generates a response string for the given prompt.

        Args:
            prompt: The formatted prompt to send to the LLM.

        Returns:
            The generated text response.
        """
        raise NotImplementedError
