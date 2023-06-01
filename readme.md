# Attendance Bot

This is a telegram attendence bot, it's run using **python 3.11** and powered with [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/), [prettytable](https://github.com/jazzband/prettytable), and [openpyxl](https://openpyxl.readthedocs.io/en/stable/#).   

> **Warning**  
> This bot will read all information available in users telegram, this bot only store `user_id`, `user_name`, `full_name`, `chat_id`, and `group_member_permission`.  
> With using this bot, user already consent to give all mentioned data. 

## Usage

> **Note**  
> Before using this bot, please invite all user into a group and give each member proper role.  
> Each member need to type `/init` or `/start` in order to use this bot properly.

### List Command
- `/start` or `/init`: Will read `user_name`, `full_name`, `user_id`, and `member_status` of the user. This command just use once when new user joined to the group.
- `/in`: Sign in, if user late it will give how many hours, minutes, and seconds the user already passed.
- `/out`: Sign out.
- `/help`: Will show this exact message.
- `/get_data {args}`: Will sent attendence report based how many days, months, or year the user supplied. Possible options are 1d, 7d, 30d, 1w, 1m, 12m, and 1y.   
E.g: `/get_data 1d`, `/get_data 7d`, `/get_data 1m`, or `/get_data 1y`.
- `/get_data_excel {args}`: Will sent attendence report in Excel format based how many days, months, or year the user supplied. Possible options are 1d, 7d, 30d, 1w, 1m, 12m, and 1y.   
E.g: `/get_data_excel 1d`, `/get_data_excel 7d`, `/get_data_excel 1m`, or `/get_data_excel 1y`.