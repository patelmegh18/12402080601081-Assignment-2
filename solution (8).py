import sys

MOD = 1_000_000_007

def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    n = int(input_data[0])
    m = int(input_data[1])

    grid = []
    idx = 2
    for _ in range(n):
        grid.append(input_data[idx:idx + m])
        idx += m

    if grid[0][0] == 'X' or grid[n - 1][m - 1] == 'X':
        print("IMPOSSIBLE")
        return

    dp_score = [[float('-inf')] * m for _ in range(n)]
    dp_paths = [[0] * m for _ in range(n)]

    dp_score[0][0] = int(grid[0][0])
    dp_paths[0][0] = 1

    directions = [(-1, 0), (0, -1), (-1, -1)]

    for r in range(n):
        for c in range(m):
            if r == 0 and c == 0:
                continue
            if grid[r][c] == 'X':
                continue

            cell_val = int(grid[r][c])
            best_prev = float('-inf')
            paths = 0

            for dr, dc in directions:
                pr, pc = r + dr, c + dc
                if 0 <= pr < n and 0 <= pc < m:
                    if dp_score[pr][pc] > best_prev:
                        best_prev = dp_score[pr][pc]
                        paths = dp_paths[pr][pc]
                    elif dp_score[pr][pc] == best_prev and best_prev != float('-inf'):
                        paths = (paths + dp_paths[pr][pc]) % MOD

            if best_prev != float('-inf'):
                dp_score[r][c] = best_prev + cell_val
                dp_paths[r][c] = paths

    if dp_score[n - 1][m - 1] == float('-inf'):
        print("IMPOSSIBLE")
    else:
        print(f"{dp_score[n - 1][m - 1]} {dp_paths[n - 1][m - 1]}")

if __name__ == '__main__':
    solve()
