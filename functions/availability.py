from llms.basic import get_llm_factory

from requests.exceptions import SSLError

# 配置LLM参数
LLM_TYPE = "tongyi"
LLM_OPTION = dict()
LLM_OPTION["model_name"] = "qwen-max"
LLM_OPTION["top_p"] = 0.9

def test_availablity():
  """
  测试程序可用性
  其中，当出现SSLError时，一般为网络中断，可以尝试重新运行。
  """
  try:
    llm = get_llm_factory(llm_type = LLM_TYPE, **LLM_OPTION)
    result = llm.invoke("What NFL team won the Super Bowl in the year Justin Bieber was born?")
    print(result)
  except SSLError as e:
    print('network broken, try again later for a short while')
  finally:
    print("test over, let's check the answer.")