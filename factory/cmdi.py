from typing import List
from httpx import Client, Response

from factory.base import BaseLLMFactory, BaseEmbeddingFactory

class CMDIFactory(BaseLLMFactory):
    ...

class CMDIEmbeddingFactory(BaseEmbeddingFactory):
    def embeddings(
        self, input: List[str],
        model: str = "bge-m3", encoding_format="float"
    ):
        client: Client = Client(
            base_url = self.base_url,
            headers  = {"Authorization": f"Bearer {self.api_key}"},
            timeout  = 30,
        )
        try:
            response: Response = client.post(
                "/embeddings",
                json={
                    "input": input,
                    "model": model,
                    "encoding_format": encoding_format,
                },
            )
            response.raise_for_status()
            results = response.json()
            if results.get("data", None) is not None:
                return results["data"][0]["embedding"]
            else:
                raise Exception(results.get("error", "Unknown error, NO DATA"))
        except Exception as e:
            return {"error": str(e)}
        finally:
            client.close()
        
    def rerank(
        self, query: str, documents: List[str],
        model: str = "bge-m3", top_n: int = 5, return_documents: bool = True
    ) -> List:
        client: Client = Client(
            base_url = self.base_url,
            headers  = {"Authorization": f"Bearer {self.api_key}"},
            timeout  = 30,
        )
        try:
            response: Response = client.post(
                "/rerank",
                json={
                    "query": query,
                    "documents": documents,
                    "model": model,
                    "top_n": top_n,
                    "return_documents": return_documents,
                },
            )
            response.raise_for_status()
            results = response.json()
            if results.get("results", None) is not None:
                return results["results"]
            else:
                raise Exception(results.get("error", "Unknown error, NO DATA"))
        except Exception as e:
            return {"error": str(e)}
        finally:
            client.close()
    
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    BGEM_URL = os.environ["BGEM_URL"]
    DEEP_URL = os.environ["DEEP_URL"]
    APPCODE = os.environ["APPCODE_KEY"]
    response = CMDIEmbeddingFactory.get_instance(
        base_url = BGEM_URL,
        api_key  = APPCODE
    ).rerank(
        query = "苹果公司的创始人是谁？",
        documents = ["苹果公司成立于1976年，由史蒂夫乔布斯、斯蒂夫·沃兹尼亚克和乔纳森·乔丹共同创建。", "苹果公司总部位于美国加利福尼亚州旧金山", "柳景兴正在吃苹果"],
        model = "bge-m3",
        top_n = 5,
        return_documents = True,
    )
    print(response)
    
    from langchain_openai.chat_models import ChatOpenAI
    with Client(
        base_url = DEEP_URL,
        headers  = {"Authorization": f"Bearer {APPCODE}"},
        timeout  = 30,
    ) as client:
        llm: ChatOpenAI = CMDIFactory.get_instance(
            base_url=DEEP_URL,
            api_key=APPCODE
        ).build(
            model = "DeepSeekR1",
            temperature = 0.7,
            max_tokens = 4096,
            client = client
        )
        # response: BaseMessage = llm.invoke([
        #     {
        #         "role": "system",
        #         "content": "You are a helpful assistant."
        #     },
        #     {
        #         "role": "user",
        #         "content": "Hello, World"
        #     }
        # ])
        # print(response.content)
        
        # from collections.abc import Iterator
        # from langchain_core.messages import BaseMessageChunk
        # import asyncio
        # response: Iterator[BaseMessageChunk] = llm.astream([
        #     {
        #         "role": "system",
        #         "content": "You are a helpful assistant."
        #     },
        #     {
        #         "role": "user",
        #         "content": "Hello, World"
        #     }
        # ])
        # for text in response:
        #     print(text.content, end = "", flush=True)
        # print()

        from collections.abc import Iterator
        from langchain_core.messages import BaseMessageChunk
        response: Iterator[BaseMessageChunk] = llm.stream([
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Hello, World"
            }
        ])
        for text in response:
            print(text.content, end = "", flush=True)
        print()