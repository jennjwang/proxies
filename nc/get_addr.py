import pandas as pd
import requests

voter_data = pd.read_csv('nc_voter_data.csv', encoding='latin1', index_col=0)

# Read the voter data in chunks
chunk_size = 5000
chunks = pd.read_csv('nc_voter_data.csv', encoding='latin1', index_col=0, chunksize=chunk_size)

# Initialize a list to store address lines for batch geocoding
i = 0
# Iterate over each chunk
for chunk in chunks:
    i += 1
    print(i)
    # Select relevant columns
    addr = chunk[['address', 'city', 'zip', 'county_name']]
    # Add state column
    addr['state'] = "NC"
    # Drop rows with any missing values
    addr.dropna(inplace=True, how="any")

    address_lines = []
    # Prepare addresses for geocoding and add to address_lines
    for index, row in addr.iterrows():
        address_lines.append(
            '%s,%s,%s,%s,%s' % (
                index,
                row['address'],
                row['city'],
                row['state'],
                row['zip']
            )
        )

    # Building the CSV file to POST
    file_contents = '\n'.join(address_lines)
    data = {
        'benchmark': 'Public_AR_Current'
    }
    files = {
        'addressFile': ('addresses.csv', file_contents)
    }

    url = 'https://geocoding.geo.census.gov/geocoder/locations/addressbatch'
    # Send request to the Census geocoding API
    response = requests.post(url, data=data, files=files)

    # Check the response
    if response.status_code == 200:
        print("Geocoding successful!")

        # Process the response
        for line in response.text.splitlines():
            parts = line.strip('"').split('","')
            address_id = int(parts[0])
            match_indicator = parts[2]
            if match_indicator == 'Match':
                code = parts[6]
                voter_data.loc[address_id, "geocode"] = code
    else:
        print("Error:", response.status_code)

# Save the geocoded data to a CSV file
voter_data.to_csv("nc_voter_data_geocode.csv")
