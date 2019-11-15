### How to run the Dashboard
 from your command line tool move into the directory of the project
- to build the docker images run command: docker-compose --file docker-compose.yml build
- to run the docker images run command: docker-compose --file docker-compose.yml up -d
- to verify that the services are running run command: docker-compose --file docker-compose.yml ps

The Dashboard is located at http://0.0.0.0:3000

to view the logs of the application that is running in the docker containers:
- for the feeder run command: docker logs --tail 100 -f feeder
- for the django dahsboard webapplication run command: docker logs --tail 100 -f django
- for the webapp service run command: docker logs --tail 100 -f webapp

The Django Admin page is located at http://0.0.0.0:5000/admin/ (Username: admin, Password: admin@123)

### Adjust config parameters
Under "Parameters" all config values are stored.
The revelant parameters for you to adjust are:
- TELEGRAM_BOT_CHAT_ID: telegram chat ID (see below)
- TELEGRAM_BOT_TOKEN: telegram bot token (see below)
- CUSTOM_TEMPLATE: telegram message template for custom S/R Levels
- CUSTOM_ALERT_SLEEP_SECONDS: sleep time of custom level alert, at most the same type of alert is sent once during that amount of seconds
- RESISTANCE_TEMPLATE: telegram message template for Resistance S/R Levels
- RESISTANCE_ALERT_SLEEP_SECONDS: sleep time of resistance level alert, at most the same type of alert is sent once during that amount of seconds
- SUPPORT_TEMPLATE: telegram message template for Support S/R Levels
- SUPPORT_ALERT_SLEEP_SECONDS: sleep time of support level alert, at most the same type of alert is sent once during that amount of seconds
- 1M_VOLUME_INCREASE_TEMPLATE: telegram message template for 1m Volume Change
- 5M_VOLUME_INCREASE_TEMPLATE: telegram message template for 5m Volume Change
- 1H_VOLUME_INCREASE_TEMPLATE: telegram message template for 1h Volume Change
- 1D_VOLUME_INCREASE_TEMPLATE: telegram message template for 1d Volume Change
- VOLUME_NUMBER_OF_TRADES: show sum of volumes of last VOLUME_NUMBER_OF_TRADES number of trades executed on BitMEX

### How to configure the Telegram Bot
**SET UP THE BOT**
- Search "botfather" in telegram
- Send "/newbot" to BotFather
- Enter a NAME for the bot
- Enter a USERNAME for the bot
- Receive the bot's TOKEN
- Get the CHAT ID via https://api.telegram.org/botTOKEN/getUpdates in the webbrowser

**PROVIDE THE CHAT ID AND TOKEN TO THE DASHBOARD**
- Log in to the Django Admin page (Username: admin, Password: admin@123)
- Go to Parameters table and update following records
- Key TELEGRAM_BOT_TOKEN, update Value field with your Telegram Bot Token
- Key TELEGRAM_BOT_CHAT_ID, update Value field with your Chat ID
- For more granular settings refer to the list of config parameters above
