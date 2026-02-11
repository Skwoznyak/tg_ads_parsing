from pydantic import BaseModel

class Phone_data(BaseModel):
    phone: str
    
    
class Channel_Data(BaseModel):
    channel_name: str