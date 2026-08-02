#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
  vector<string> input;
  string s;
  while (cin >> s) {
    input.push_back(s);
  }
  sort(input.begin(), input.end(), [](const string &a, const string &b) { return a + b > b + a; });
  string result;
  for (const string &piece: input) {
    result += piece;
  }
  cout << result << endl;
  return 0;
}
