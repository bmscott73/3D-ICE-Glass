import os

# Define the target directories in sequence
TARGET_FOLDERS = [
    "e4"
]
OUTPUT_FILENAME = "e4_hausen_master_combined.txt"

def build_master_file():
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as outfile:
        for folder in TARGET_FOLDERS:
            if not os.path.exists(folder):
                print(f"Skipping '{folder}': Directory not found.")
                continue

            # Write folder section header
            outfile.write(f"=== {folder} content ===\n\n")
            
            # Sort files for predictable order
            files = sorted(os.listdir(folder))
            
            for file_name in files:
                # Filter for .txt files and exclude tmap files
                if not file_name.endswith(".txt") or "tmap" in file_name.lower():
                    continue

                file_path = os.path.join(folder, file_name)

                # Write individual file header
                outfile.write(f"--- {file_name} ---\n")

                # Read and append the file's contents
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as infile:
                        content = infile.read()
                        outfile.write(content)
                        # Ensure content ends with a newline before separating
                        if not content.endswith("\n"):
                            outfile.write("\n")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

                # Spacing newline between files
                outfile.write("\n")

    print(f"Successfully generated {OUTPUT_FILENAME}")

if __name__ == "__main__":
    build_master_file()