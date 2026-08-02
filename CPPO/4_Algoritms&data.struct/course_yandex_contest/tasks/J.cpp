#include <deque>
#include <iostream>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;

    deque<int> left, right;

    for (int i = 0; i < N; i++) {
        char op;
        cin >> op;

        if (op == '+') {
            int x;
            cin >> x;
            right.push_back(x);

            if (right.size() > left.size()) {
                left.push_back(right.front());
                right.pop_front();
            }
        } else if (op == '*') {
            int x;
            cin >> x;

            if (left.size() > right.size()) {
                right.push_front(x);
            } else {
                left.push_back(x);
            }
            if (left.size() > right.size() + 1) {
                right.push_front(left.back());
                left.pop_back();
            }
        } else if (op == '-') {
            cout << left.front() << '\n';
            left.pop_front();

            if (left.size() < right.size()) {
                left.push_back(right.front());
                right.pop_front();
            }
        }
    }

    return 0;
}
