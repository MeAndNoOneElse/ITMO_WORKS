#include <algorithm>
#include <iostream>
#include <vector>
using namespace std;

int main() {
  int n, k;
  cin >> n >> k;
  vector<int> stalls(n);
  for (int i = 0; i < n; i++) {
    cin >> stalls[i];
  }
  int left = 0;
  int right = stalls[n - 1] - stalls[0];
  int answer = 0;
  while (left <= right) {
    int mid = (left + right) / 2;
    int cows = 1;
    int last_pos = stalls[0];
    for (int i = 1; i < n; i++) {
      if (stalls[i] - last_pos >= mid) {
        cows++;
        last_pos = stalls[i];
      }
    }
    if (cows >= k) {
      answer = mid;
      left = mid + 1;
    } else {
      right = mid - 1;
    }
  }
  cout << answer << endl;
  return 0;
}
