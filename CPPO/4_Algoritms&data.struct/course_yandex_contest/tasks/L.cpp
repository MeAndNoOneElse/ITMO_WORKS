#include <deque>
#include <iostream>
#include <vector>

using namespace std;

int main() {
  int N, K;
  cin >> N >> K;

  vector<int> arr(N);
  for (int i = 0; i < N; i++) {
    cin >> arr[i];
  }

  deque<int> dq;  // хранит индексы элементов в порядке возрастания значений

  for (int i = 0; i < N; i++) {
    if (!dq.empty() && dq.front() <= i - K) {
      dq.pop_front();
    }

    while (!dq.empty() && arr[dq.back()] >= arr[i]) {
      dq.pop_back();
    }
    dq.push_back(i);

    if (i >= K - 1) {
      cout << arr[dq.front()];
      if (i < N - 1) {
        cout << " ";
      }
    }
  }

  cout << "\n";

  return 0;
}
