from google.adk.models.lite_llm import LiteLlm

def lite_llm_model():
    """
    Returns the hardcoded language model name.

    Returns:
        The hardcoded model name string.
    """

    # hard code model name
    return "gemini-2.5-flash"

    # if model_name.startswith("gemini"):
    #     return model_name
    # else:
    #     return LiteLlm(model=model_name)
