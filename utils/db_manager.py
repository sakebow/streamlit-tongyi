import re
import inspect
from functools import wraps
from datetime import datetime
from typing import ClassVar, Any
from sqlalchemy import create_engine, text

from utils.common import DBManager

class ElectricOrderItemDBManager(DBManager):
    base_type: ClassVar[str] = "ElectricOrderItem"
    link: ClassVar[str] = 'sqlite:///order.db'
    local_generator: ClassVar[Any] = None

    """
    自定义PyMyBatis
    """
    def __init__(self):
        ElectricOrderItemDBManager.local_generator = self.import_class_from_package("vo", self.base_type)
    def search(self, query_template):
        def decorator(func):
            # 解析 SQL 中的 #{变量} 语法
            param_pattern = re.compile(r"#{(\w+)}")
            required_params = set(param_pattern.findall(query_template))

            @wraps(func)
            def wrapper(*args, **kwargs):
                # 获取函数的参数签名
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                # 提取传递的参数，包括 **kwargs 中的参数
                provided_params = set(bound_args.arguments.keys()) | set(kwargs.keys())
                # 检查缺失的参数
                missing_params = required_params - provided_params
                if missing_params:
                    raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
                # 构建 SQL 语句，并考虑不同类型的数据格式
                sql_query = text(query_template.replace("#{", ":").replace("}", ""))
                print(f"Executing SQL: {sql_query}")
                params = bound_args.arguments.copy()
                for key, value in params.items():
                    if isinstance(value, datetime):
                        params[key] = value.strftime('%Y-%m-%d')
                engine = create_engine(self.link)
                with engine.connect() as conn:
                    result = conn.execute(sql_query, bound_args.arguments)
                    search_result = [self.create_item_obj(row) for row in result]
                return search_result
            return wrapper
        return decorator

if __name__ == "__main__":
    edbm = ElectricOrderItemDBManager()

    class BatisManager:
        def __init__(self):
            self.results = None
        @edbm.search("SELECT * FROM item_list WHERE order_year = #{order_year}")
        def search_items_by_year(self, order_year: int):
            ...

    b = BatisManager()
    print(b.search_items_by_year(2023))