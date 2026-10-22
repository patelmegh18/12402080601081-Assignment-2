import sys
import re
from collections import defaultdict

EMAIL_PATTERN = re.compile(r'(?i)\b([a-z0-9._%+-]+)@([a-z0-9.-]+\.(?:com|edu|org))\b')

def parse_emails(file_path):
    domain_users = defaultdict(set)
    domain_emails = defaultdict(list)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for username, domain in EMAIL_PATTERN.findall(line):
                domain = domain.lower()
                full_email = f"{username}@{domain}"
                domain_users[domain].add(username.lower())
                domain_emails[domain].append(full_email)

    for domain in sorted(domain_users.keys()):
        unique_count = len(domain_users[domain])
        smallest_email = min(domain_emails[domain])
        print(f"{domain} {unique_count} {smallest_email}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        parse_emails(sys.argv[1])
    else:
        path = input("Enter file path: ").strip()
        parse_emails(path)
