import os
from http import HTTPStatus
from dashscope import TextEmbedding
from typing import List, Dict, Union
from pymilvus.client.types import ExtraList
from pymilvus.milvus_client.index import IndexParams
from pymilvus import MilvusClient, FieldSchema, CollectionSchema, DataType

from factory.base import BaseLLMFactory, BaseEmbeddingFactory

class TongyiFactory(BaseLLMFactory):
    ...

class TongyiEmbeddingFactory(BaseEmbeddingFactory):
    def _embedding(
        self, input: str,
        model: str = TextEmbedding.Models.text_embedding_v3,
        dimension: int = 1024
    ) -> List[float]:
        """
        调用`dashscope`的文本`embedding`服务
        本段完全摘自`dashscope`的官方文档
        """
        resp = TextEmbedding.call(
            model = model,
            input = input,
            dimension = dimension,
            api_key=st.secrets["DASHSCOPE_API_KEY"],
        )
        if resp.status_code == HTTPStatus.OK:
            return resp.output["embeddings"][0]["embedding"]
        else:
            return []
    
    def _create_or_replace(
        self,  milvus_client: MilvusClient, db_file_name: str, collection_name: str,
        dimension: int = 1024, data: List[str] = None
    ) -> MilvusClient:
        """
        创建搜索样本库
        """
        # 为了简化操作，直接本地创建搜索样本库，并采用覆盖创建的方式
        db_file_path = f"{db_file_name}.db"
        if milvus_client is None or not os.path.exists(db_file_path):
            milvus_client = MilvusClient(db_file_path)
        if milvus_client.has_collection(collection_name = collection_name):
            milvus_client.drop_collection(collection_name = collection_name)
        # 创建集合
        milvus_client.create_collection(
            collection_name = collection_name, dimension = dimension,
            metric_type="IP",  # Inner product distance
            consistency_level="Strong",  # Strong consistency level
            # 创建集合`schema`
            schema = CollectionSchema(fields=[
                ## 下面三个字段来自`milvus`官网的`example`
                ### `id`字段，自增（手动）主键，标记当前句子是第几个
                FieldSchema(
                    name = "id", dtype = DataType.INT64,
                    is_primary = True, description = "primary key"
                ),
                ### `embeddings`字段，存储当前句子的向量
                FieldSchema(
                    name = "embeddings", dtype = DataType.FLOAT_VECTOR,
                    description = "embeddings", dim = dimension
                ),
                ### `text`字段，存储句子本身
                FieldSchema(
                    name = "text", dtype = DataType.VARCHAR,
                    description = "text", max_length = 65535
                )
            ], description = "data schema")
        )
        # 创建集合索引，创建后才可以使用`IP`搜索策略
        index_params = IndexParams()
        ## 主要针对`embeddings`字段创建索引
        index_params.add_index(
            field_name = "embeddings", index_type = "IVF_FLAT",
            index_name = "embeddings"
        )
        milvus_client.create_index(
            collection_name = collection_name, index_params = index_params
        )
        # 插入数据
        if data is not None:
            milvus_client.insert(collection_name = collection_name, data = data)
        return milvus_client
    
    def _embedding_search(
        self,
        milvus_client: MilvusClient, collection_name: str, question: str, top_k: int = 5
    ) -> List[Dict]:
        """
        搜索向量
        """
        result = milvus_client.search(
            collection_name = collection_name,
            anns_field = "embeddings",  # 指定搜索的向量字段名（关键参数）
            data = [self._embedding(input = question)], # 输入搜索向量
            limit = top_k,
            output_fields = ["text"],
        )
        """
        result输出：
        data: ["[
            {'id': 0, 'distance': 0.7548444271087646, 'entity': {'text': ...}},
            {'id': 1, 'distance': 0.7238685488700867, 'entity': {'text': ...}},
            {'id': 3, 'distance': 0.6937779784202576, 'entity': {'text': ...}}, ...]
        "]
        因此解包需要指定返回第一个结果
        """
        return result[0]

    def embeddings(
        self, input: List[str],
        model: str = TextEmbedding.Models.text_embedding_v3,
        dimension: int = 1024
    ) -> List[Dict[str, Union[int, str, List[float]]]]:
        embeddings: List = [
            {
                "id": idx,
                "embeddings": self._embedding(s, model, dimension),
                "text": s
            }
            for idx, s in enumerate(input)
        ]
        return embeddings
        
    def rerank(
        self, query: str, documents: List[str],
        model: str = TextEmbedding.Models.text_embedding_v3,
        db_file: str = "rag_test", collection_name: str = "demo",
        dimension: int = 1024, top_n: int = 5,
    ):
        embeddings: List = self.embeddings(documents, model)
        milvus_client: MilvusClient = None
        milvus_client = self._create_or_replace(
            milvus_client, db_file, collection_name, dimension, embeddings
        )
        response: ExtraList = self._embedding_search(
            milvus_client = milvus_client,
            collection_name = collection_name,
            question = query,
            top_k = top_n
        )
        return response

if __name__ == "__main__":
    import streamlit as st
    response: List = TongyiEmbeddingFactory.get_instance(
        base_url = st.secrets["DASH_URL"],
        api_key = st.secrets["DASHSCOPE_API_KEY"],
    ).rerank(
        query = "苹果公司的创始人是谁？",
        documents = ["苹果公司成立于1976年，由史蒂夫乔布斯、斯蒂夫·沃兹尼亚克和乔纳森·乔丹共同创建。", "苹果公司总部位于美国加利福尼亚州旧金山", "柳景兴正在吃苹果"],
        top_n = 5
    )
    print(response)
    # from langchain_openai.chat_models.base import ChatOpenAI
    # llm: ChatOpenAI = TongyiFactory.get_instance(
    #     base_url=st.secrets["DASH_URL"],
    #     api_key=st.secrets["DASHSCOPE_API_KEY"]
    # ).build(
    #     model = "qwen-max",
    # )
    # from langchain_core.messages import BaseMessage
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
    # response: Iterator[BaseMessageChunk] = llm.stream([
    #     {
    #         "role": "system",
    #         "content": "You are a helpful assistant."
    #     },
    #     {
    #         "role": "user",
    #         "content": "Hello, World"
    #     }
    # ])
    # for chunk in response:
    #     print(chunk.content)