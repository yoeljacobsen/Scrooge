import urllib.request
import zipfile
import os
import io

def download_and_extract(filename_zip, filename_csv, num_lines=100):
    url = f"https://raw.githubusercontent.com/phoebetronic/mnist/main/{filename_zip}"
    print(f"Downloading {filename_zip} from {url}...")
    
    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", filename_csv)
    
    try:
        response = urllib.request.urlopen(url)
        zip_data = response.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            # Find the CSV file inside the zip
            csv_name = [name for name in zf.namelist() if name.endswith('.csv')][0]
            print(f"Extracting sample from {csv_name} in {filename_zip}...")
            with zf.open(csv_name) as csv_file:
                lines = []
                for _ in range(num_lines + 1):
                    line = csv_file.readline()
                    if not line:
                        break
                    lines.append(line.decode('utf-8'))
                    
        with open(out_path, "w") as f:
            f.writelines(lines)
            
        print(f"Successfully saved sample to {out_path}")
    except Exception as e:
        print(f"Error processing {filename_zip}: {e}")

if __name__ == "__main__":
    download_and_extract("mnist_train.csv.zip", "mnist_train.csv")
    download_and_extract("mnist_test.csv.zip", "mnist_test.csv")
