from google.adk.models.lite_llm import LiteLlm

def lite_llm_model(model_name: str = "gemini-2.0-flash"):
    """
    Returns a language model instance based on the provided model name.

    Args:
        model_name (str): The name of the model to instantiate.
        If None or empty, defaults to "gemini-2.5-flash".

    Returns:
        An instance of the specified language model.
    """

    # hard code model name 
    return "gemini-2.5-flash"

    # if model_name.startswith("gemini"):
    #     return model_name
    # else:
    #     return LiteLlm(model=model_name)
