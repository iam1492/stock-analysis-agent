from google.adk.models.lite_llm import LiteLlm

def lite_llm_model(model_name: str = "gemini/gemini-2.0-flash"):
    """
    Returns a language model instance based on the provided model name.

    Args:
        model_name (str): The name of the model to instantiate.

    Returns:
        An instance of the specified language model.
    """

    if model_name is None:
        model_name = "gemini/gemini-2.0-flash"

    model_name = "gemini/gemini-2.5-flash-preview-09-2025"

    return LiteLlm(model=model_name)
