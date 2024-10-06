import wixData from 'wix-data';
import wixLocation from 'wix-location';
import {fetch} from 'wix-fetch'; // Import fetch from wix-fetch

const OPENCAGE_API_KEY = '0e51a978a3484e8cb7880d8ec27cc079';

$w.onReady(function () {
    // Initially disable the submit button
    $w("#button35").disable();

    // Add an event listener for changes in the address input field
    $w("#addressInput1").onChange(() => {
		console.log("read"); //Checking if address has been input
        // Get the value of the address input
        let address = $w("#addressInput1").value;

        // Validate the address input
        if (address !== "") {
            // If the address is valid, enable the submit button
            $w("#button35").enable();
        } else {
            // If the address is invalid, disable the button and show an error message
            $w("#button35").disable();
			console.log("invalid address"); //Checking if invalid address input
        }
    });

	// Handle the submit button click
	$w("#button35").onClick(async () => {
		console.log("Button pressed");
		const address = $w("#addressInput1").value.formatted;

		try {
			const latLong = await getLatLong(address);
			console.log(latLong); // latLong checking

			const latLongData = {
				"latitude": latLong.lat,
				"longitude": latLong.lng,
                "addressField": latLong.city
			};

			// Insert latitude and longitude into Addresses collection
			await wixData.insert("Addresses", latLongData);
			
			// Query database for parameters
			const result = await queryDatabase(latLong);

			if (result) {
                const referenceLocation = {
                    "newLat" : parseFloat(result.lat.toFixed(3)),
                    "newLong" : parseFloat(result.long.toFixed(3))
                };
                const newAdd = await getAddress(referenceLocation);

				const soyParametersData = {
					"title": result.title,
                    "maturityGroup": result["Soybean Maturity Group"],
                    "referenceAddress" : newAdd
				};
                console.log(soyParametersData.title);
				// Insert soy parameters into Items collection
				await wixData.insert("Items", soyParametersData);

                wixLocation.to('/seed');
            } 
		} catch (err) {
			console.error("Error: ", err);
		}
	});

    // Function to get latitude and longitude using OpenCage Geocoding API
    function getLatLong(address) {
        const apiUrl = `https://api.opencagedata.com/geocode/v1/json?q=${encodeURIComponent(address)}&key=${OPENCAGE_API_KEY}`;
        return fetch(apiUrl)
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then((data) => {
                if (data.results && data.results.length > 0) {
                    const location = data.results[0].geometry;
                    const country = data.results[0].components
                    return {
                        lat: location.lat,
                        lng: location.lng,
                        city: `${country.city}, ${country.country}`
                    };
                } else {
                    throw new Error("No results found");
                }
            });
    }

    function queryDatabase(latLong) {
        const apiUrl = 'https://c095-137-132-26-33.ngrok-free.app/data'; // Replace with your server's API endpoint and end with '/data'
        return fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                //'Authorization': 'Bearer 2n2szgBdyv3VDrzdhhq19zrw0j5_7nEbgELpCMZUH6QwBAXdq'
            },
            body: JSON.stringify({
                latitude: latLong.lat,
                longitude: latLong.lng
            })
        })
        .then((response) => {
            if (!response.ok) {
				console.log("Database not ok :(");
                throw new Error("Network was not ok");
            }
            return response.json();
        })
        .then((data) => {
			console.log("Database successfully contacted!");
            console.log(data);
            return data; // Return the matching data from the server
        })
        .catch((err) => {
            console.error("Error querying database: ", err);
            return null;
        });
    }

    async function getAddress(latLong) {
        const apiUrl = `https://api.opencagedata.com/geocode/v1/json?q=${latLong.lat}+${latLong.lng}&key=${OPENCAGE_API_KEY}`;
        return fetch(apiUrl)
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then((data) => {
                if (data.results && data.results.length > 0) {
                    const city = data.results[0].components.city;
                    const country = data.results[0].components.country;
                    return `${city}, ${country}`;
                } else {
                    throw new Error("No results found");
                }
            });        

    }
});
