from datetime import datetime

from vo.obj_item import ObjItem

class ElectricOrderItem(ObjItem):
    """
    订单类
    """
    def __init__(self, id: int = None,
        order_year: int = None, border_id: str = None, contract_num: str = None, order_depart: str = None, proj_name: str = None,
        item_code: str = None, item_name: str = None, item_num: int = None, item_money: float = None, item_send: datetime = None,
        order_start: datetime = None, item_repeat: str = None
    ):
        """
        对照数据库表构建字段
        """
        self.id = id if id else None
        self.order_year = order_year if order_year else None
        self.border_id = border_id if border_id else None
        self.contract_num = contract_num if contract_num else None
        self.order_depart = order_depart if order_depart else None
        self.proj_name = proj_name if proj_name else None
        self.item_code = item_code if item_code else None
        self.item_name = item_name if item_name else None
        self.item_num = item_num if item_num else None
        self.item_money = item_money if item_money else None
        self.item_send = item_send if item_send else None
        self.order_start = order_start if order_start else None
        self.item_repeat = item_repeat if item_repeat else None