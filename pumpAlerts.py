import colorlog, logging
import os
import yaml

from alerter import BinancePumpAndDumpAlerter
from sender import TelegramSender


def duration_to_seconds(duration):
    unit = duration[-1]
    if unit == "s":
        unit = 1
    elif unit == "m":
        unit = 60
    elif unit == "h":
        unit = 3600

    return int(duration[:-1]) * unit


# Read config
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
yaml_file = open(os.path.join(__location__, "config.yml"), "r", encoding="utf-8")
config = yaml.load(yaml_file, Loader=yaml.FullLoader)

# Define the log format
bold_seq = "\033[1m"
log_format = "[%(asctime)s] %(levelname)-8s %(name)-25s %(message)s"
color_format = f"{bold_seq} " "%(log_color)s " f"{log_format}"

colorlog.basicConfig(
    # Define logging level according to the configuration
    level=logging.DEBUG if config["debug"] is True else logging.INFO,
    # Declare the object we created to format the log messages
    format=color_format,
    # Declare handlers for the Console
    handlers=[logging.StreamHandler()],
)

# Define your own logger name
logger = logging.getLogger("binance-pump-alerts-app")

# Logg whole configuration during the startup
logger.debug("Config: %s", config)

telegram = TelegramSender(
    token=config["telegramToken"],
    chat_id=config["telegramChatId"],
    alert_chat_id=config["telegramAlertChatId"]
    if "telegramAlertChatId" in config and config["telegramAlertChatId"] != 0
    else config["telegramChatId"],
    retry_interval=duration_to_seconds(config["telegramRetryInterval"]),
    bot_emoji=config["botEmoji"],
    pump_emoji=config["pumpEmoji"],
    dump_emoji=config["dumpEmoji"],
    top_emoji=config["topEmoji"],
    new_listing_emoji=config["newListingEmoji"],
)

alerter = BinancePumpAndDumpAlerter(
    api_url=config["apiUrl"],
    watchlist=[] if "watchlist" not in config else config["watchlist"],
    pairs_of_interest=config["pairsOfInterest"],
    chart_intervals=config["chartIntervals"],
    outlier_intervals=config["outlierIntervals"],
    top_report_intervals=config["topReportIntervals"],
    extract_interval=duration_to_seconds(config["extractInterval"]),
    retry_interval=duration_to_seconds(config["priceRetryInterval"]),
    reset_interval=duration_to_seconds(config["resetInterval"]),
    top_pump_enabled=config["topPumpEnabled"],
    top_dump_enabled=config["topDumpEnabled"],
    additional_statistics_enabled=config["additionalStatsEnabled"],
    no_of_reported_coins=config["noOfReportedCoins"],
    dump_enabled=config["dumpEnabled"],
    check_new_listing_enabled=config["checkNewListingEnabled"],
    telegram=telegram,
)
alerter.run()
