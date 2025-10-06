import pandas as pd
import io
import requests

sheets = {"Alluvial soil":"1n6t9yRVvEZeanX4eCHjlGq66PEIvbWnXnv_vfTPUB4s",
          "Black Soil": "1-Y6SOflkN-nth7S5t3GyMJDr_acqcxUHjekUcjS5IfU",
          "Clay soil":"1Lt2u9OokNdcwXu9fVmkRJ64L7c6GVOQAVEa97LZsKfg",
          "Red soil":"1n-90FiHvBOOmT8K5rbd7U1k-8aqwMyoKfAY5zsF0yjE"}

def load_soil_plants(soil_type):
    print("Requested soil type:", soil_type)

    file_id = sheets[soil_type]
    dwn_url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv'

    try:
        response = requests.get(dwn_url)
        response.raise_for_status()

        csv_data = io.StringIO(response.text)
        df = pd.read_csv(csv_data)

        df.columns = df.columns.str.strip().str.lower()
        
        if not {"plants", "care_tips", "season"}.issubset(df.columns):
            print(f"Columns missing in sheet for {soil_type}")
            return []

        combined = []
        for _, row in df.iterrows():
            combined.append({
                "name": str(row["plants"]).strip(),
                "tip": str(row["care_tips"]).strip(),
                "season": str(row["season"]).strip()
            })

        return combined
    

    except Exception as e:
        print("Error loading plants:", e)
        return []