from openai import OpenAI

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI()

    def embed(self, text: str):
        return self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        ).data[0].embedding

    def embed_batch(self, texts: list[str]):
        return [
            self.client.embeddings.create(
                model="text-embedding-3-small",
                input=t
            ).data[0].embedding
            for t in texts
        ]