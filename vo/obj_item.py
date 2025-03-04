class ObjItem:
    """
    支持字典化（序列化）父类
    """
    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key, value
    def __getitem__(self, key):
        return getattr(self, key)
    def keys(self):
        return self.__dict__.keys()