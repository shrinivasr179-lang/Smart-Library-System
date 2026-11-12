
import statistics
import csv

# Library book issue counts
book_data = {
    "Python": 20,
    "Java": 15,
    "DBMS": 25,
    "AI": 30,
    "Networking": 15,
    "Operating Systems": 10,
    "Blockchain": 35
}

values = list(book_data.values())

print("\n===== LIBRARY STATISTICS MODULE =====")

print("\nBook Issue Data:")
for book, count in book_data.items():
    print(book, ":", count)

print("\nMean:", statistics.mean(values))
print("Median:", statistics.median(values))
print("Mode:", statistics.multimode(values))
print("Variance:", statistics.variance(values))
print("Standard Deviation:", statistics.stdev(values))
print("Minimum:", min(values))
print("Maximum:", max(values))

# Save data to CSV
with open("library_statistics.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Book", "Issue_Count"])

    for book, count in book_data.items():
        writer.writerow([book, count])

print("\nData saved to library_statistics.csv")
print("\nStatistics module completed successfully!")