import json
import csv
import os

# Directory containing the JSON files
json_dir = "./articles/"  # Change this to the folder where your JSON files are stored
output_csv = "nature_articles.csv"

ML_TECHNIQUES = {
    "Traditional ML": ["regression", "decision tree", "svm", "k-means"],
    "DNN": ["cnn", "rnn", "lstm", "deep learning"],
    "Gen AI": ["transformer", "gan", "diffusion model", "bert"]
}

SECURITY_PRIVACY = {
    "Attack Types": ["evasion", "poisoning", "backdoor", "membership inference", "model inversion", "data reconstruction", "untargeted poisoning", "energy latency attack"],
    "Attacker Identity": ["patient", "healthcare practitioner", "ml service provider", "3rd-party healthcare organization", "cybercriminals", "business competitors"],
    "Attacker Capability": ["training data control", "model control", "testing data control", "query access", "explanation access"]
}

# Columns for the CSV file
csv_columns = [
    "title", "link", "publication_date", "abstract",
    "conclusions", f"ml_techniques: (ex: {[(k, v) for k, v in ML_TECHNIQUES.items()]})", f"security_privacy: (ex: {[(k, v) for k, v in SECURITY_PRIVACY.items()]})"
]

def json_to_csv(json_dir, output_csv):
    # Collect all JSON files in the directory
    json_files = [f for f in os.listdir(json_dir) if f.endswith(".json")]

    # Prepare the CSV file
    with open(output_csv, mode="w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()

        # Iterate through each JSON file
        for json_file in json_files:
            json_path = os.path.join(json_dir, json_file)
            with open(json_path, mode="r", encoding="utf-8") as f:
                articles = json.load(f)

                for article in articles:
                    # Prepare the row for the CSV
                    row = {
                        "title": article.get("title", ""),
                        "link": article.get("link", ""),
                        "publication_date": article.get("publication_date", ""),
                        "abstract": article.get("abstract", ""),
                        "conclusions": article.get("conclusions", ""),
                        f"ml_techniques: (ex: {[(k, v) for k, v in ML_TECHNIQUES.items()]})": ", ".join(article.get("ml_techniques", [])),
                        f"security_privacy: (ex: {[(k, v) for k, v in SECURITY_PRIVACY.items()]})": "; ".join(
                            f"{key}: {', '.join(values)}"
                            for key, values in article.get("security_privacy", {}).items()
                        )
                    }

                    # Write the row to the CSV
                    writer.writerow(row)

    print(f"CSV file saved to {output_csv}")

# Run the script
json_to_csv(json_dir, output_csv)
