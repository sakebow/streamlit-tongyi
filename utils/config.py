from typing import Sequence

class DefaultCommonConfig(enumerate):
  DIMENSION: int = 1024
  SPLIT_PATTERN_LIST: Sequence = ["\n", "\n\n"]

  DATABASE_NAME: str = "rag_test"
  COLLECTION_NAME: str = "demo"

  SUPPORT_TYPES = ["txt", "pdf"]