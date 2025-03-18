
class LLM:
    def __init__(self, api_key):
        self.api_key = api_key
    def generate(self, prompt="", image_path=None, model_name=None, needwaiting = True):
        raise NotImplementedError
    async def async_generate(self, prompt="", image_path=None, model_name="None", needwaiting = True):
        raise NotImplementedError





