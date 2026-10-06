#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> a(n);
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }

    ll ans = 0;

    for (int l = 0; l < n; l++) {
        map<int, int> bits;
        map<map<int, int>, int> seen;

        for (int r = l; r < n; r++) {
            // Инкрементально добавляем элемент a[r]
            bits[a[r]]++;

            // Нормализуем: преобразуем в битовое представление
            auto it = bits.find(a[r]);
            while (it != bits.end() && it->second >= 2) {
                int pos = it->first;
                int cnt = it->second;
                bits[pos + 1] += cnt / 2;
                bits[pos] = cnt % 2;

                if (bits[pos] == 0) {
                    bits.erase(pos);
                }
                it = bits.find(pos + 1);
            }

            // Удаляем нули
            for (auto it = bits.begin(); it != bits.end();) {
                if (it->second == 0) {
                    it = bits.erase(it);
                } else {
                    ++it;
                }
            }

            // Если это новое состояние
            if (seen.find(bits) == seen.end()) {
                seen[bits] = 1;
                if (bits.size() == 1) {
                    ans++;
                }
            }
        }
    }
    cout << ans;
    return 0;
}
