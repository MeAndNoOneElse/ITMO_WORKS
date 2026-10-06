#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;

int main() {
  string s;
  cin >> s;
  vector<long long> weights(26);
  for (int i = 0; i < 26; i++) {
    cin >> weights[i];
  }
  int n = s.length();
  vector<int> freq(26, 0);
  for (char c: s) {
    freq[c - 'a']++;
  }
  vector<pair<long long, char> > letters;
  for (int i = 0; i < 26; i++) {
    if (freq[i] > 0) {
      letters.push_back({weights[i], char('a' + i)});
    }
  }
  sort(
    letters.begin(),
    letters.end(),
    [](const pair<long long, char> &a, const pair<long long, char> &b) {
      return a.first > b.first;
    }
  );
  vector<char> result(n);
  int left = 0, right = n - 1;
  vector<char> middle;
  for (auto &p: letters) {
    char c = p.second;
    int count = freq[c - 'a'];
    if (count == 1) {
      middle.push_back(c);
    } else if (count >= 2) {
      result[left++] = c;
      result[right--] = c;
      for (int i = 2; i < count; i++) {
        middle.push_back(c);
      }
    }
  }
  int mid_index = left;
  for (char c: middle) {
    result[mid_index++] = c;
  }
  for (char c: result) {
    cout << c;
  }
  cout << endl;
  return 0;
}
