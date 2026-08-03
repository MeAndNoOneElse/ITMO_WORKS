import sys
from pyramid import mode_pyramid
from marker import mode_marker_tracking
from rubiks_new import mode_rubiks_cube


def show_menu():
    print("\n" + "=" * 50)
    print("LAB 8 - OpenCV")
    print("=" * 50)
    print("1 - Image pyramid")
    print("2 - Marker tracking")
    print("3 - Rubik's cube tracking")
    print("0 - Exit")
    print("=" * 50)


def main():
    modes = {
        '1': mode_pyramid,
        '2': mode_marker_tracking,
        '3': mode_rubiks_cube
    }

    while True:
        show_menu()
        choice = input("\nSelect: ").strip()

        if choice == '0':
            print("пара-пара-пара-пам ВСЁ!")
            sys.exit(0)
        elif choice in modes:
            modes[choice]()
            input("\nPress Enter to continue...")
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()

