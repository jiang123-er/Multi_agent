"""
    配置日志文件目的：1. 排查问题（最核心的目的）
                  2.监控程序运行状态（没有日志：你不知道它是正常运行、还是卡住了、还是处理了多少请求）
                  3.追溯操作和责任
                    如果程序是多人使用 / 团队维护（比如求职后做的企业级项目）：
                    没有日志：出了问题说不清 “是谁在什么时候操作了什么”。
                    有配置好的日志：能记录 [用户A] [2026-02-16 19:00] [执行了删除数据操作]，
                    方便追溯操作记录，定位责任，也能恢复误操作的数据。
                  4.可控的日志管理（配置的价值）
                    代码里配置日志格式、指定日志目录，就是为了让日志 “好用”：
                    统一格式：所有日志长得一样，不管是看还是用工具分析，都不混乱；
                    指定存储位置：日志都存在 logs 文件夹里，不会散落在电脑各处，方便查找、清理（比如日志文件太大了，定期删）；
                    分级记录：可以配置只记录 ERROR 级别的关键错误，或者记录 INFO 级别的日常运行信息，按需调整，不会让日志文件又大又乱
"""
import os
from util.path_tool import get_abs_path
#导入python的日志模块
import logging
from datetime import datetime
#日志保存根目录
LOG_ROOT = get_abs_path("logs")
#确认日志目录的存在
os.makedirs(LOG_ROOT,exist_ok= True)

#日志格式配置 error错误 info日常信息 debug废话模型
DEFAULT_LOG_FORMAT = logging.Formatter(
    #这是日志的输出格式模板，用 %()s 的形式占位       见名知意即可
    # %(asctime)s    : 日志产生的时间
    # %(name)s       : 日志器的名字
    # %(levelname)s  : 日志级别（如 INFO、ERROR、DEBUG）
    # %(filename)s   : 产生这条日志的文件名
    # %(lineno)d     : 产生这条日志的代码行号
    # %(message)s    : 日志的具体内容
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
def get_logger(
    name:str = 'agent',
    console_level:int = logging.INFO,
    file_level:int = logging.DEBUG,
    log_file = None,
) -> logging.Logger :
    #创建日志管理器
    logger = logging.getLogger(name)
    #设置日志级别
    logger.setLevel(logging.DEBUG)

    #避免重复添加到Handler（控制台）
    if logger.handlers: #日志文件存放路径
        return logger
    #控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)

    if not log_file:
        log_file = os.path.join(LOG_ROOT,f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file,encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT )

    logger.addHandler(file_handler)
    return logger

logger = get_logger()

if __name__ == '__main__':
    logger.info('信息日志')
    logger.error('错误日志')
    logger.warning('警告日志')
    logger.debug('调试日志')
