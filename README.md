Run: python cron_parser.py "arg"

Example: python cron_parser.py "0-30/5 * * * * /usr/bin/find"

Expected result: 

minute        0 5 10 15 20 25 30
hour          0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
day of month  1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
month         1 2 3 4 5 6 7 8 9 10 11 12
day of week   0 1 2 3 4 5 6
command       /usr/bin/find
