# Attendance Bot

This is a telegram attendence bot, it's run using **python 3.11** and powered with [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/), [prettytable](https://github.com/jazzband/prettytable), [mysql](https://pypi.org/project/mysql-connector-python/), [pytz](https://pythonhosted.org/pytz/), and [openpyxl](https://openpyxl.readthedocs.io/en/stable/#).   

> **Warning**  
> This bot will read all information available in users telegram, this bot only store `user_id`, `user_name`, `full_name`, `chat_id`, and `group_member_permission`, `channel_id`.  
> With using this bot, user already consent to give all mentioned data.   
> This bot didn't read and write any chat other than assigned group room, private room and channel room.

## Server Usage   

Before using this bot you need to prepare your database, this bot used `MySQL` as it database. You need to create tables which are listed below:
 - absensi: It will contains all the attendence.
 - userlist: It will contains all basic user information, such as: `username`, `full_name`, `userid`, `admin_status`, `active_user_status`. `signin_time_limit`.
 - approval: It will contains all user approval.
 - room: It will contains all room information, such as: `chat_id`, `username`, `room_type`. 
 
After the database has been setup, you need to install `python 3.11` and `pip3` after all python has been installed you need downloads all dependency using `pip3 install -r requirement.txt`. After all dependency installed you can run with command (Linux): `nohup python3 -u main.py &` and for stop the bot (Linux): `kill -9 "ps ax | grep 'python3' | awk '{print $1}' | head -1"`

## Client Usage

> **Note**  
> Before using this bot, please invite all user into a group and a channel. Give each member a proper role.   
> Make sure each user has his/her telegram username set !  
> Invite the bot into a group and channel.   
> Each member need to type `/init` or `/start` in order to use this bot properly.   
> You needed to set room for channel by using `/set_room` command.   
> If channel has been set, every day at 6 o'clock in the evening the bot will sent a report for today attendance to the channel
> Optional: You needed to set each member sign in time default 07:00:00 (7 a.m), you can change it using `/set_in_time {telegram_username} {hh:mm:ss}`. E.g: `/set_in_time Xx_mentorkuadmin_xX 09:30:45`.   

### List Command
- `/start` or `/init`: Will read `user_name`, `full_name`, `user_id`, and `member_status` of the user. This command just use once when new user joined to the group.
- `/in`: Sign in, if user late it will give how many hours, minutes, and seconds the user already passed.
- `/out`: Sign out.
- `/help`: Will show this exact message.
- `/get_data {args}`: Will sent attendence report based how many days, months, or year the user supplied. Possible options are now, 1d, 7d, 30d, 1w, 1m, 12m, and 1y. If no argument were given it will sent today attendence report.   
E.g: `/get_data`, `/get_data 1d`, `/get_data 7d`, `/get_data 1m`, or `/get_data 1y`.
- `/get_data_excel {args}`: Will sent attendence report in Excel format based how many days, months, or year the user supplied. Possible options are now, 1d, 7d, 30d, 1w, 1m, 12m, and 1y. If no argument were given it will sent today attendence report.   
E.g: `/get_data_excel`, `/get_data_excel 1d`, `/get_data_excel 7d`, `/get_data_excel 1m`, or `/get_data_excel 1y`.
- `/sick`: Sick leave.
- `/leave {args}`: On leave status, it is require how many days the user wanted to take its leave. This command will sent a notification to the channel and the leave must be accepted by the supervisior. (Max: 3 days and didn't take any leave within one month span).
E.g: `/leave 2d`.
- `/set_in_time {args0} {args1}`: Will set user's sign in time, this will determine if the user late or on time. it's required telegram username and sign in time with format hh:mm:ss.
E.g: `/set_in_time Xx_ment0rKu_Adm1n_xX 08:00:00`.
- `/get_log` : Will fetch log data from `mentorku.log` to the chat.
- `/set_password`: Set passsword for accessing dashboard (Ongoing development). It will asked to fill a form which must be filled. For canceling use `/cancel`.
- `/get_approval {args}`: Will display all pending specific user approval to chat. If no argument given it will print all pending user approval. E.g: `/get_approval`, `/get_approval Xx_Ment0rKuAdm1n_xX`.
- `/init_room`: Will record room or channel id. Must be used after invited bot into the channel.