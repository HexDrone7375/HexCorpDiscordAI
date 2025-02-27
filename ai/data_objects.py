from typing import Iterable, Optional
from discord import Attachment


class MessageCopy:
    '''
    This class is instantiated at the start of the on_message chain in main.py.
    It copies all important attributes required to proxy a message.
    At the end of the on_message chain, the message original and message copy are compared.
    If they are not identical, the original is deleted and the copy is proxied via webhook.
    '''
    def __init__(
        self,
        content: Optional[str] = None,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        attachments: Iterable[Attachment] = []
    ):
        self.content = content
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.attachments = attachments
