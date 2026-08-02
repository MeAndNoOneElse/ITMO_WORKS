#include <algorithm>
#include <iostream>
#include <set>
#include <vector>

using namespace std;

int main() {
  int N, K, P;
  cin >> N >> K >> P;
  vector<int> seq(P);
  for (int i = 0; i < P; i++) {
    cin >> seq[i];
    seq[i]--;
  }
  vector<int> next_pos(P, P + 1);
  vector<int> last_occurrence(N, P + 1);
  for (int i = P - 1; i >= 0; i--) {
    int car = seq[i];
    next_pos[i] = last_occurrence[car];
    last_occurrence[car] = i;
  }

  set<pair<int, int> > on_floor;
  vector<bool> on_floor_flag(N, false);
  vector<int> current_next(N, P + 1);
  int operations = 0;

  for (int i = 0; i < P; i++) {
    int car = seq[i];

    if (on_floor_flag[car]) {
      on_floor.erase({current_next[car], car});
      current_next[car] = next_pos[i];
      on_floor.insert({current_next[car], car});
    } else {
      operations++;

      if ((int) on_floor.size() == K) {
        auto it = prev(on_floor.end());
        int removed_car = it->second;
        on_floor.erase(it);
        on_floor_flag[removed_car] = false;
        current_next[removed_car] = P + 1;
      }

      current_next[car] = next_pos[i];
      on_floor.insert({current_next[car], car});
      on_floor_flag[car] = true;
    }
  }

  cout << operations << endl;
  return 0;
}
