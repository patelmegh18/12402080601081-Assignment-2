import sys
import re
from collections import deque, defaultdict

LOG_REGEX = re.compile(r'^(\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(FAIL|SUCCESS)$')

def to_minutes(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

def process_logs():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    x, t = map(int, input_data[0].split())
    n = int(input_data[1])
    logs = input_data[2:2 + n]

    failures = defaultdict(deque)
    suspicious_users = {}

    for line in logs:
        match = LOG_REGEX.match(line.strip())
        if not match:
            continue
        ts, user, ip, status = match.groups()
        current_time = to_minutes(ts)

        q = failures[user]
        while q and (current_time - q[0][0]) > t:
            q.popleft()

        if status == 'FAIL':
            q.append((current_time, ip))
        elif status == 'SUCCESS':
            if len(q) >= x:
                recent_ips = {item[1] for item in q}
                if ip not in recent_ips:
                    if user not in suspicious_users:
                        suspicious_users[user] = ts
            q.clear()

    for user in sorted(suspicious_users.keys()):
        print(f"{user} {suspicious_users[user]}")

if __name__ == '__main__':
    process_logs()
