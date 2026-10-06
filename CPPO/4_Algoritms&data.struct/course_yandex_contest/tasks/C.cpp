#include <iostream>
#include <stack>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(nullptr);

  unordered_map<string, long long> vars;
  stack<vector<pair<string, long long> > > restore_stack;

  string line;
  while (getline(cin, line)) {
    if (line == "{") {
      restore_stack.push({});
    } else if (line == "}") {
      auto &top = restore_stack.top();
      for (int i = (int) top.size() - 1; i >= 0; --i) {
        vars[top[i].first] = top[i].second;
      }
      restore_stack.pop();
    } else {
      size_t pos = line.find('=');
      string lhs = line.substr(0, pos);
      string rhs = line.substr(pos + 1);

      bool is_number = !rhs.empty() &&
                       (isdigit((unsigned char) rhs[0]) || rhs[0] == '-');

      long long new_val;
      if (is_number) {
        new_val = stoll(rhs);
      } else {
        new_val = vars[rhs];
        cout << new_val << "\n";
        cout.flush();
      }

      if (!restore_stack.empty()) {
        restore_stack.top().push_back({lhs, vars[lhs]});
      }
      vars[lhs] = new_val;
    }
  }
  return 0;
}
