from bot import Bot, config, logger

if __name__ == "__main__":
    bot = Bot(
        debug=config.DEBUG,
        logger_cls=logger,
        logger_level=config.LOG_LEVEL,
        test_guilds=config.BOT_TEST_DISCORD_GUILD_IDS,
    )
    bot.i18n.load(config.PATH_LOCALE)
    bot.load_extensions(config.PATH_COGS)
    bot.run(config.BOT_TOKEN)
