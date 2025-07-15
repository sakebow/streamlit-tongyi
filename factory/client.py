from threading import Lock
from typing import ClassVar, Optional

from httpx import Client, AsyncClient, Timeout

from factory.base import BaseFactory

class ClientFactory(BaseFactory):

    # ---------- 共享资源 ----------
    _sync_client: ClassVar[Optional[Client]] = None
    _async_client: ClassVar[Optional[AsyncClient]] = None
    _client_lock: ClassVar[Lock] = Lock()

    # ===== 私有方法：懒加载 httpx 客户端 =====
    def _ensure_clients(self) -> None:
        if self._sync_client is None:
            with self._client_lock:
                if self._sync_client is None:
                    ClientFactory._sync_client = Client(
                        base_url=self.base_url,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        timeout=Timeout(self.timeout)
                    )
                    ClientFactory._async_client = AsyncClient(
                        base_url=self.base_url,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        timeout=Timeout(self.timeout)
                    )

    # ===== 对外接口 =====
    def client(self) -> Client:
        self._ensure_clients()
        return self._sync_client

    def async_client(self) -> AsyncClient:
        self._ensure_clients()
        return self._async_client

# ------------------ 使用示例 ------------------
if __name__ == "__main__":
    f1 = ClientFactory.get_instance(
        base_url="https://api.example.com",
        api_key="sk-xxxx",
        timeout=30,
    )
    f2 = ClientFactory.get_instance(
        base_url="https://api.sakebow.com",
        api_key="sk-xxxx",
        timeout=30,
    )
    print(f1.client())
    print(f2.client())
    print(f1.client().base_url)
    
