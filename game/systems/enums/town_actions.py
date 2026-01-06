from enum import Enum

class Town_Actions(Enum):
    ENTER_INN        = "enter inn"
    ENTER_TAVERN     = "enter tavern"
    ENTER_SHOP       = "enter shop"
    LEAVE_BUILDING   = "leave building"
    REST             = "rest"
    TALK             = "talk"
    ENTER_CAVE       = "enter cave"
    ENTER_CASTLE     = "enter castle"
    LEAVE_TOWN       = "leave town"
    BUY_BEER         = "buy beer"
    BUY_FROM_SHOP    = "buy from shop"
    SELL_FROM_SHOP   = "sell from shop"
