#include <iostream>
#include <vector>
using namespace std;
int main() {
    int n;
    cin >> n;
    vector<int> keyIn(n);
    for (int i = 0; i < n; i++) {
        cin >> keyIn[i];
        keyIn[i]--;
    }
    vector<int> state(n, 0);
    int cycles = 0;
    for (int i = 0; i < n; i++) {
        if (state[i] == 0) {
            int cur = i;
            while (state[cur] == 0) {
                state[cur] = 1;
                cur = keyIn[cur];
            }
            if (state[cur] == 1) {
                cycles++;
            }
            cur = i;
            while (state[cur] != 2) {
                state[cur] = 2;
                cur = keyIn[cur];
            }
        }
    }
    cout << cycles << endl;
    return 0;
}
