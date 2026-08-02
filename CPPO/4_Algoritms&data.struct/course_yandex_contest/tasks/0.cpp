#include <iostream>
#include <string>

using namespace std;

int main() {
  int ttt = 0;
  cin >> ttt;

  for (int i = 0; i < ttt; i++) {
    string ass;
    cin >> ass;

    size_t len = ass.size();

    if (len % 2 != 0) {
      cout << "NO" << '\n';
      continue;
    }
    size_t half = len / 2;
    string first = ass.substr(0, half);
    string second = ass.substr(half, len);

    if (first == second) {
      cout << "YES" << '\n';
    } else {
      cout << "NO" << '\n';
    }
  }
  return 0;
}
