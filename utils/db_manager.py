import re
import inspect
import importlib
from functools import wraps
from datetime import datetime
from typing import ClassVar, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine.row import Row

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
    def import_class_from_package(self, package_name, class_name):
        _package = importlib.import_module(package_name)
        if class_name not in _package.__all__:
            raise ImportError(f"{class_name} not found in {package_name}")
        cls = getattr(_package, class_name)
        if cls is not None:
            return cls
        else:
            raise ImportError(f"{class_name} not found in {package_name}")
    def create_item_obj(self, row: Row):
        return self.local_generator(**row._asdict()) if self.local_generator else None
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
                sql_query = query_template
                for param in required_params:
                    if param in kwargs:  
                        value = kwargs[param]
                    else:  
                        value = bound_args.arguments.get(param)

                    # 处理不同数据类型
                    if isinstance(value, str):  # 字符串需要加引号
                        formatted_value = f"'{value}'"
                    elif isinstance(value, (int, float)):  # 数值直接替换
                        formatted_value = str(value)
                    elif isinstance(value, datetime):  # 日期时间转换格式
                        formatted_value = f"'{value.strftime('%Y-%m-%d')}'"
                    else:
                        raise TypeError(f"Unsupported parameter type for {param}: {type(value)}")
                    sql_query = sql_query.replace(f"#{{{param}}}", formatted_value)
                print(f"Executing SQL: {sql_query}")
                engine = create_engine(self.link)
                with engine.connect() as conn:
                    result = conn.execute(text(sql_query))
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