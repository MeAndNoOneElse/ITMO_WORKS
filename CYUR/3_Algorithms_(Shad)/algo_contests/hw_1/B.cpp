#include <iostream>
#include <string>
#include <vector>

static bool IsOpenBracket(char bracket_char) {
    return (bracket_char == '(') || (bracket_char == '[') ||
           (bracket_char == '{');
}

static bool IsCloseBracket(char bracket_char) {
    return (bracket_char == ')') || (bracket_char == ']') ||
           (bracket_char == '}');
}

static char GetMatchingOpen(char bracket_char) {
    if (bracket_char == ')') {
        return '(';
    }
    if (bracket_char == ']') {
        return '[';
    }
    if (bracket_char == '}') {
        return '{';
    }
    return '\0';
}

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::string bracket_string;
    std::cin >> bracket_string;

    std::vector<char> stack;
    int max_prefix = 0;

    for (size_t index = 0; index < bracket_string.size(); ++index) {
        char current_char = bracket_string[index];
        if (IsOpenBracket(current_char)) {
            stack.push_back(current_char);
        } else if (IsCloseBracket(current_char)) {
            if (stack.empty() ||
                GetMatchingOpen(current_char) != stack.back()) {
                max_prefix = static_cast<int>(index);
                break;
            }
            stack.pop_back();
        }
        max_prefix = static_cast<int>(index + 1);
    }

    if (stack.empty() &&
        max_prefix == static_cast<int>(bracket_string.size())) {
        std::cout << "CORRECT\n";
    } else {
        std::cout << max_prefix << "\n";
    }

    return 0;
}
