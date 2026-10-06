#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
  int n, k;
  cin >> n >> k;
  vector<int> nums(n);
  for (int i = 0; i < n; i++) {
    cin >> nums[i];
  }
  sort(nums.begin(), nums.end(), greater<int>());
  long result = 0;
  for (int i = 0; i < n; i++) {
    if ((i + 1) % k != 0) {
      result += nums[i];
    }
  }
  cout << result << endl;
  return 0;
}
