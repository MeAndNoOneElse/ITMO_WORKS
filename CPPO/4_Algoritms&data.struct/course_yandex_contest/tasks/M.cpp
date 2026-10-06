#include <algorithm>
#include <iostream>
#include <queue>
#include <vector>
using namespace std;
int main() {
  int n, m, sx, sy, fx, fy;
  cin >> n >> m >> sx >> sy >> fx >> fy;
  sx--;
  sy--;
  fx--;
  fy--;
  vector<string> a(n);
  for (int i = 0; i < n; i++)
    cin >> a[i];
  vector<vector<int>> d(n, vector<int>(m, 1e9));
  vector<vector<pair<int, int>>> p(n, vector<pair<int, int>>(m, {-1, -1}));
  priority_queue<pair<int, pair<int, int>>> q;
  d[sx][sy] = 0;
  q.push({
      0, {sx, sy}
  });
  int dx[] = {-1, 1, 0, 0}, dy[] = {0, 0, 1, -1};
  char dir[] = {'N', 'S', 'E', 'W'};
  while (!q.empty()) {
    int x = q.top().second.first;
    int y = q.top().second.second;
    q.pop();
    for (int i = 0; i < 4; i++) {
      int nx = x + dx[i], ny = y + dy[i];
      if (nx < 0 || nx >= n || ny < 0 || ny >= m)
        continue;
      if (a[nx][ny] == '#')
        continue;
      int cost = (a[nx][ny] == '.') ? 1 : 2;
      if (d[x][y] + cost < d[nx][ny]) {
        d[nx][ny] = d[x][y] + cost;
        p[nx][ny] = {x, y};
        q.push({
            -d[nx][ny], {nx, ny}
        });
      }
    }
  }
  if (d[fx][fy] == 1e9) {
    cout << -1;
    return 0;
  }
  string path;
  int x = fx, y = fy;
  while (x != sx || y != sy) {
    int px = p[x][y].first, py = p[x][y].second;
    for (int i = 0; i < 4; i++) {
      if (px + dx[i] == x && py + dy[i] == y) {
        path += dir[i];
        break;
      }
    }
    x = px;
    y = py;
  }
  reverse(path.begin(), path.end());
  cout << d[fx][fy] << "\n" << path;
}
