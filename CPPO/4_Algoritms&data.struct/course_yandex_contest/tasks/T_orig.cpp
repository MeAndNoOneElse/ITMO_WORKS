#include <iostream>
#include <map>
#include <set>
#include <vector>
using namespace std;
using ll = long long;

const ll P = 1e18;

// Функция для быстрого возведения в степень по модулю
ll power_mod(ll base, ll exp, ll mod) {
    ll result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (__int128)result * base % mod;
        }
        base = (__int128)base * base % mod;
        exp /= 2;
    }
    return result;
}

ll ans = 0;

// Структура для хранения информации о сумме и её частоте
map<ll, int> cnt_left, cnt_right;

void solve(vector<ll>& a, int l, int r) {
    if (l == r) {
        // Проверяем, является ли одиночный элемент степенью 2
        ll val = a[l];
        int bit_count = __builtin_popcountll(val);
        if (bit_count == 1) {
            ans++;
        }
        return;
    }

    int mid = (l + r) / 2;

    // Рекурсивные вызовы для левой и правой половин
    solve(a, l, mid);
    solve(a, mid + 1, r);

    // Объединение результатов
    cnt_left.clear();
    cnt_right.clear();

    // Количество бит, которое может быть в итоговой сумме
    int max_bit = 60;

    // Заполняем все возможные степени 2 по модулю P
    set<ll> powers_of_two;
    ll pow2 = 1;
    for (int i = 0; i <= max_bit; i++) {
        powers_of_two.insert(pow2 % P);
        pow2 = (__int128)pow2 * 2 % P;
    }

    // Обработка левой половины (от mid к l)
    ll sum = 0;
    for (int i = mid; i >= l; i--) {
        sum = (sum + a[i]) % P;
        cnt_left[sum]++;
    }

    // Обработка правой половины (от mid+1 к r)
    sum = 0;
    for (int i = mid + 1; i <= r; i++) {
        sum = (sum + a[i]) % P;
        cnt_right[sum]++;
    }

    // Для каждой левой суммы и каждой степени 2
    for (auto& [left_sum, left_count] : cnt_left) {
        for (ll power : powers_of_two) {
            // Нужная сумма для правой части
            ll needed = (power - left_sum + P) % P;
            if (cnt_right.count(needed)) {
                ans += (ll)left_count * cnt_right[needed];
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<ll> a(n);
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        // a[i] = 2^x mod P
        a[i] = power_mod(2, x, P);
    }

    solve(a, 0, n - 1);

    cout << ans << endl;

    return 0;
}

