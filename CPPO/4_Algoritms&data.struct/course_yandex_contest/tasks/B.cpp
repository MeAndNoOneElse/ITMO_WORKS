#include <cctype>
#include <iostream>
#include <stack>
#include <string>
#include <vector>

using namespace std;

int main() {
  string s;
  cin >> s;
  int n = s.length() / 2;

  vector<int> result(n, -1);

  stack<tuple<char, int, bool> > st;

  int animal_cnt = 0;
  int trap_cnt = 0;

  for (int i = 0; i < 2 * n; i++) {
    char c = s[i];
    bool is_animal = islower(c) != 0;
    char lower = tolower(c);

    if (!st.empty()) {
      auto [top_char, top_idx, top_is_animal] = st.top();
      if (top_char == lower && top_is_animal != is_animal) {
        int animal_idx, trap_idx;
        if (top_is_animal) {
          animal_idx = top_idx;
          trap_idx = trap_cnt;
        } else {
          animal_idx = animal_cnt;
          trap_idx = top_idx;
        }
        result[trap_idx] = animal_idx + 1;
        st.pop();
        if (is_animal)
          animal_cnt++;
        else
          trap_cnt++;
        continue;
      }
    }

    if (is_animal) {
      st.push({lower, animal_cnt, true});
      animal_cnt++;
    } else {
      st.push({lower, trap_cnt, false});
      trap_cnt++;
    }
  }

  if (!st.empty()) {
    cout << "Impossible" << endl;
    return 0;
  }

  cout << "Possible" << endl;
  for (int i = 0; i < n; i++) {
    cout << result[i];
    if (i < n - 1)
      cout << " ";
  }
  cout << endl;

  return 0;
}
