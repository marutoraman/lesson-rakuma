### Amazonからの商品情報取得処理を記述
from common.logger import set_logger
logger = set_logger(__name__)

class Amazon(object):
    
    def __init__(self) -> None:
        logger.info("ログ出力テスト")