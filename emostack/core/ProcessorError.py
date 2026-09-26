class ProcessorError(Exception):
    """A call to the LLM model or the embedder failed, or its answer could not be read."""
