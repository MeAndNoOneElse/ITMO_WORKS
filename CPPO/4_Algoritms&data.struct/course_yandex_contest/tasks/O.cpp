#include <iostream>
#include <vector>
using namespace std;
vector<vector<int>> g;
vector<int> color;
bool ok = true;
void dfs(int v, int c) {
    color[v] = c;
    for (int to : g[v]) {
        if (color[to] == 0) {
            dfs(to, 3 - c);
        } else if (color[to] == c) {
            ok = false;
            return;
        }
    }
}
int main() {
    int n, m;
    cin >> n >> m;
    g.resize(n + 1);
    color.assign(n + 1, 0);
    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        g[a].push_back(b);
        g[b].push_back(a);
    }
    for (int i = 1; i <= n; i++) {
        if (color[i] == 0) {
            dfs(i, 1);
        }
    }
    cout << (ok ? "YES" : "NO");
    return 0;
}
