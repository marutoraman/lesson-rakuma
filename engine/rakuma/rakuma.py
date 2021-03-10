### ラクマ出品処理を記述
from common.logger import set_logger
logger = set_logger(__name__)

class Rakuma(object):
    
    def __init__(self) -> None:
        logger.info("ログ出力テスト")