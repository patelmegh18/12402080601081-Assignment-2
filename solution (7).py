import sys
import json

def parse_stream(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                yield record, True
            except json.JSONDecodeError:
                yield None, False

def run_etl(file_path):
    stats = {}

    for record, is_valid in parse_stream(file_path):
        if not is_valid or not isinstance(record, dict):
            continue

        device_id = record.get('device_id')
        if not device_id:
            continue

        if device_id not in stats:
            stats[device_id] = {
                'count': 0,
                'min': float('inf'),
                'max': float('-inf'),
                'sum': 0.0,
                'corrupted': 0
            }

        temp = record.get('temperature_c')
        if temp is None or not isinstance(temp, (int, float)):
            stats[device_id]['corrupted'] += 1
            continue

        temp = float(temp)
        dev = stats[device_id]
        dev['count'] += 1
        dev['sum'] += temp
        if temp < dev['min']:
            dev['min'] = temp
        if temp > dev['max']:
            dev['max'] = temp

    for device in sorted(stats.keys()):
        d = stats[device]
        if d['count'] > 0:
            avg = d['sum'] / d['count']
            min_val = int(d['min']) if d['min'].is_integer() else d['min']
            max_val = int(d['max']) if d['max'].is_integer() else d['max']
            print(f"{device} count={d['count']} min={min_val} max={max_val} avg={avg:.2f} corrupted={d['corrupted']}")
        else:
            print(f"{device} count=0 min=0 max=0 avg=0.00 corrupted={d['corrupted']}")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'sensors.jsonl'
    run_etl(target)
