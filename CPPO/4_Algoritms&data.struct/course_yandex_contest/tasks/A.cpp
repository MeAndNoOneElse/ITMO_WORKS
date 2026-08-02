#include <iostream>
#include <vector>

using namespace std;

int main() {
  int n = 0;
  cin >> n;
  vector<int> a(n);
  for (int i = 0; i < n; i++) {
    cin >> a[i];
  }

  int left = 0;
  int max_len = 1;
  int best_left = 0;
  int count = 1;
  for (int right = 1; right < n; right++) {
    if (a[right] == a[right - 1]) {
      count++;
    } else {
      count = 1;
    }
    if (count == 3) {
      left = right - 1;
      count = 2;
    }
    int current_len = right - left + 1;
    if (current_len > max_len) {
      max_len = current_len;
      best_left = left;
    }
  }
  cout << best_left + 1 << " " << best_left + max_len << endl;

  return 0;
}
