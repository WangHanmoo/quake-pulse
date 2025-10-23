# main.py
import fetch_usgs
import process_data
import visualize_map
import polar_quake

if __name__ == "__main__":
    print("Fetching earthquake data...")
    data = fetch_usgs.fetch_usgs()
    df = process_data.geojson_to_df(data)

    print("Choose visualization type:")
    print("1 - World Map")
    print("2 - Polar Artistic Animation")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        visualize_map.visualize_quakes_on_map(df)
    elif choice == "2":
        polar_quake.polar_visualization(df)
    else:
        print("Invalid choice.")
