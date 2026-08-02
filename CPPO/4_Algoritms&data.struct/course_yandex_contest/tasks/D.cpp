#include <iostream>
#include <map>
#include <vector>

using namespace std;

int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(nullptr);
  long long a, b, c, d, k;
  cin >> a >> b >> c >> d >> k;
  vector<long long> history;
  map<long long, long long> seen;

  long long cur = a;
  for (long long day = 1; day <= k; ++day) {
    if (seen.count(cur)) {
      long long cycle_start = seen[cur];
      long long cycle_len = day - cycle_start;
      long long offset = (k - cycle_start) % cycle_len;
      cout << history[cycle_start - 1 + offset] << "\n";
      return 0;
    }
    seen[cur] = day;
    cur = cur * b;
    if (cur < c) {
      cout << 0 << "\n";
      return 0;
    }
    cur -= c;
    cur = min(cur, d);
    history.emplace_back(cur);
    if (cur == 0) {
      cout << 0 << "\n";
      return 0;
    }
  }
  cout << history.back() << "\n";
  return 0;
}
