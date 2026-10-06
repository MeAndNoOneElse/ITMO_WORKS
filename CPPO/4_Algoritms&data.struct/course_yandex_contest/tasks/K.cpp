#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <random>
#include <set>

using namespace std;
typedef int ll;
typedef long double ld;
typedef string str;

void f() {
  ios::sync_with_stdio(0);
  cin.tie(0);
  cout.tie(0);
}

int main() {
  f();
  ll n, m;
  cin >> n >> m;
  set<pair<ll, ll> > a;
  map<ll, ll> b;
  map<ll, ll> c;
  map<ll, pair<ll, ll> > q;
  a.insert({n, 0});
  b[0] = n;
  c[n - 1] = n;
  for (ll s = 1; s <= m; ++s) {
    ll x;
    cin >> x;
    if (x > 0) {
      if (ll(a.size()) == 0) {
        cout << -1 << "\n";
        q[s] = {-1, -1};
        continue;
      }
      ll z = a.rbegin()->first, y = a.rbegin()->second;
      if (z == x) {
        cout << y + 1 << "\n";
        q[s] = {z, y};
        a.erase({z, y});
        b.erase(y);
        c.erase(y + z - 1);
      } else if (z > x) {
        cout << y + 1 << "\n";
        q[s] = {x, y};
        a.erase({z, y});
        b.erase(y);
        c.erase(y + z - 1);
        a.insert({z - x, y + x});
        b[y + x] = z - x;
        c[y + z - 1] = z - x;
      } else {
        cout << -1 << "\n";
        q[s] = {-1, -1};
      }
    } else {
      x = -x;
      auto v = q[x];
      if (v.first == -1 && v.second == -1) {
        continue;
      } else {
        if (c.count(v.second - 1) > 0) {
          pair<ll, ll> z = {v.second - 1, c[v.second - 1]};
          c.erase(v.second - 1);
          a.erase({z.second, z.first - z.second + 1});
          b.erase(z.first - z.second + 1);
          v.first += z.second;
          v.second = z.first - z.second + 1;
        }
        if (b.count(v.second + v.first) > 0) {
          pair<ll, ll> y = {v.second + v.first, b[v.second + v.first]};
          b.erase(v.second + v.first);
          a.erase({y.second, y.first});
          c.erase(y.first + y.second - 1);
          v.first += y.second;
        }
        a.insert(v);
        b[v.second] = v.first;
        c[v.second + v.first - 1] = v.first;
      }
    }
  }
  return 0;
}
