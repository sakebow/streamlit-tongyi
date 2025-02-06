from typing import List

class DefaultCommonConfig(enumerate):
  DIMENSION: int = 1024
  SPLIT_PATTERN_LIST: List = ["\n", "\n\n"]

  DATABASE_NAME: str = "rag_test"
  COLLECTION_NAME: str = "demo"