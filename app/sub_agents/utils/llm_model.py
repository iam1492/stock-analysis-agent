from google.adk.models.lite_llm import LiteLlm

def lite_llm_model(model_name: str = "gemini-2.0-flash"):
    """
    Returns a language model instance based on the provided model name.

    Args:
        model_name (str): The name of the model to instantiate.

    Returns:
        An instance of the specified language model.
    """

    #model_name = "gemini-2.5-pro"
    model_name = "gemini-2.5-flash"
    #model_name = "openrouter/z-ai/glm-4.6"
    #model_name = "openrouter/qwen/qwen3-max"
    
    if model_name.startswith("gemini"):
        return model_name
    else:
        return LiteLlm(model=model_name)
