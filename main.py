# main.py
import fetch_usgs
import process_data
import visualize_map
import aurora_quake

if __name__ == "__main__":
    print("Fetching earthquake data...")
    data = fetch_usgs.fetch_usgs()
    df = process_data.geojson_to_df(data)

    print("\nSelect visualization mode:")
    print("1. Map visualization")
    # print("2. Classic animation")
    print("2. Aurora Quake")

    choice = input("Enter 1 / 2: ")

    if choice == "1":
        print("Launching map visualization...")
        visualize_map.visualize(df)

    elif choice == "2":
        print("Launching Aurora Quake visualization...")
        aurora_quake.aurora_visualization(df)

    else:
        print("Invalid choice. Exiting.")


