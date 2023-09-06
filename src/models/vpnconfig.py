import os, sys, datetime
sys.path.append(os.getcwd())

from outline_vpn.outline_vpn import OutlineVPN
from sqlalchemy.types import BIGINT, TEXT, BOOLEAN, Integer
from sqlalchemy import Column, ForeignKey, select

from src.configs.config import WG_SERVER_RUS_LINK, WG_SERVER_NETH_LINK, OUTLINE_SERVER_RUS_LINK, OUTLINE_SERVER_NETH_LINK, VOLUMELIMIT
from src.configs.utils import wg, easy_error_handler
from src.db.db import session_scope
from src.models.base import Base


class VPNConfig(Base):

    __tablename__ = 'vpn_configs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(BIGINT, ForeignKey('users.uid'))
    wg_rus_config = Column(TEXT)
    wg_neth_config = Column(TEXT)
    outline_rus_config = Column(TEXT)
    outline_neth_config = Column(TEXT)
    is_blocked = Column(BOOLEAN)


    def __init__(
            self, uid: int, wg_rus_config: int=None, wg_neth_config: int=None, 
            outline_rus_config: int=None, outline_neth_config: int=None, is_blocked: bool=False
        ) -> None:

        self.uid = uid
        self.wg_rus_config = wg_rus_config
        self.wg_neth_config = wg_neth_config
        self.outline_rus_config = outline_rus_config
        self.outline_neth_config = outline_neth_config
        self.is_blocked = is_blocked
        

    def __repr__(self) -> str:
        return '<%s(uid=%s, wg_rus_config=%s, wg_neth_config=%s, outline_rus_config=%s, outline_neth_config=%s, is_blocked=%s)>' % \
            (self.__class__.__name__, self.uid, self.wg_rus_config, self.wg_neth_config, 
             self.outline_rus_config, self.outline_neth_config, self.is_blocked)
    

    @classmethod
    @easy_error_handler
    async def get_data(cls, uid: int=None) -> list[object | None]:
        '''Получение данных с таблицы '''
        
        async with session_scope() as async_session:
            query = None
            if not uid:
                query = select(cls)
            elif uid:
                query = select(cls).where(cls.uid==uid)
            
            if query:
                vpnconfigs = await async_session.execute(query)
                vpnconfigs = [result[0] for result in vpnconfigs.all()]
                return vpnconfigs
            return []
    
    @classmethod
    @easy_error_handler
    async def add_data(cls, user: int, config: object, column: str, configs: list[object]) -> None:
        '''Добавление данных в таблицы '''

        async with session_scope() as async_session:
            if column == 'outline_rus_config':
                if configs:
                    configs[0].outline_rus_config = config
                    async_session.add(configs[0])
                else:
                    new_config = cls(uid=user.uid, outline_rus_config=config) 
                    async_session.add(new_config)
            elif column == 'outline_neth_config':
                if configs:
                    configs[0].outline_neth_config = config
                    async_session.add(configs[0])
                else:
                    new_config = cls(uid=user.uid, outline_neth_config=config) 
                    async_session.add(new_config)
            elif column == 'wg_rus_config':
                if configs:
                    configs[0].wg_rus_config = config
                    async_session.add(configs[0])
                else:
                    new_config = cls(uid=user.uid, wg_rus_config=config) 
                    async_session.add(new_config)
            elif column == 'wg_neth_config':
                if configs:
                    configs[0].wg_neth_config = config
                    async_session.add(configs[0])
                else:
                    new_config = cls(uid=user.uid, wg_neth_config=config) 
                    async_session.add(new_config)


    @staticmethod
    @easy_error_handler
    async def make_config(user, data='config') -> str:
        '''Создание конфицурации VPN на сервере'''

        links = {
            'make_configs_wg_rus_btn': WG_SERVER_RUS_LINK,
            'make_configs_wg_neth_btn': WG_SERVER_NETH_LINK,
            'make_configs_outline_rus_btn': OUTLINE_SERVER_RUS_LINK, 
            'make_configs_outline_neth_btn': OUTLINE_SERVER_NETH_LINK
        }
        link = links.get(data, None)

        if data in ('make_configs_wg_rus_btn', 'make_configs_wg_neth_btn'):
            config = await wg('add', link, user.uid)
        else:
            client = OutlineVPN(api_url=link)
            new_key = client.create_key()
            timestamp = round(datetime.datetime.timestamp(datetime.datetime.now()))
            client.rename_key(new_key.key_id, f'{timestamp} Ключ {new_key.key_id} - {user.uid}, {user.fullname}')
            config = f'{new_key.key_id}##{new_key.access_url}'
        return config


    @easy_error_handler
    async def off_configs(self) -> None:
        '''Отключение VPN на сервере конкретного клиента'''

        if self.wg_rus_config:
            await wg('off', WG_SERVER_RUS_LINK, self.uid)
        
        if self.wg_neth_config:
            await wg('off', WG_SERVER_NETH_LINK, self.uid)
        
        if self.outline_rus_config:
            client = OutlineVPN(api_url=OUTLINE_SERVER_RUS_LINK)
            client.add_data_limit(self.outline_rus_config.split('##')[0], 1024 * 1024 * int(VOLUMELIMIT))
        
        if self.outline_neth_config:
            client = OutlineVPN(api_url=OUTLINE_SERVER_NETH_LINK)
            client.add_data_limit(self.outline_neth_config.split('##')[0], 1024 * 1024 * int(VOLUMELIMIT))
        
        self.is_blocked = True


    @easy_error_handler
    async def on_configs(self)-> None:
        '''Включение VPN на сервере конкретного клиента'''

        if self.wg_rus_config:
            await wg('on', WG_SERVER_RUS_LINK, self.uid)
        if self.wg_neth_config:
            await wg('on', WG_SERVER_NETH_LINK, self.uid)
        if self.outline_rus_config:
            client = OutlineVPN(api_url=OUTLINE_SERVER_RUS_LINK)
            client.delete_data_limit(self.outline_rus_config.split('##')[0])
        if self.outline_neth_config:
            client = OutlineVPN(api_url=OUTLINE_SERVER_NETH_LINK)
            client.delete_data_limit(self.outline_neth_config.split('##')[0])
        self.is_blocked = False


    @easy_error_handler
    async def get_debug() -> str:
        '''Получение статуса работы WG c сервере'''

        wg_rus = await wg(command = 'debug', link = WG_SERVER_RUS_LINK)
        wg_neth = await wg(command = 'debug', link = WG_SERVER_NETH_LINK)
        return wg_rus, wg_neth