How to use the application!

1. pull data from MERRA2!
    https://disc.gsfc.nasa.gov/datasets/M2T1NXFLX_5.12.4/summary?keywords=MERRA-2%20tavg1_2d_flx_Nx
    MERRA-2 tavg1_2d_flx_Nx: 2d,1-Hourly,Time-Averaged,Single-Level,Assimilation,Surface Flux Diagnostics V5.12.4 (M2T1NXFLX)
        MERRA-2 was chosen due to its multiple sensors and its high number of weather related sensors, 
    Select desired dates from the database, the current implementation of the code takes data from once every 2 weeks to reduce the db size

    To pull data from the API, fill in username and password in, rename the .txt file to the .txt generated, running pull_satelliteData.py will create a folder MERRA2_Files which will house all the .nc4 files

2. Generating base dataset
    To generate the reference_data, run faster_reference_data_generate.py
    It extracts geographical data from filtered_usa_points.csv, creating reference_data_set.json which documents geographical data with their respecive suggested Soy bean variants

3. Run backend_logic to run the backend 
    without UI, can simply call the function from backed to get most similar conditions, the code for backend functionality is commented out

4. front end is hosted on wix, JS code is included on the github aswell
5. 
![Homepage](https://github.com/[Hong-yiii]/[MR_BEAN]/blob/[main]/Homepage.png?raw=true)
![Output Page](https://github.com/[Hong-yiii]/[MR_BEAN]/blob/[main]/output_page.png?raw=true)
