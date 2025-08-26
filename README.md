# Customer Platform Health Check
This Customer_Platform_Health_Check.exe provides a health check utility for managing and monitoring a customer platform. It performs various checks, such as database connectivity, license validation, disk space monitoring, and service statuses, while generating an HTML report summarizing the results.

### Features
- **Database Connection Check**: Validates connectivity to a PostgreSQL database (CSS).
- **License Key Validation**: Verifies license keys in both CSS and the AIP console.
- **Disk Space Monitoring**: Ensures sufficient disk space for all the attached drives.
- **Service Checks**: Monitors AIP Console version, services like HDED, and imaging status.
- **HTML Report Generation**: Creates an HTML report summarizing health checks.

### Prerequisites
To run Customer_Platform_Health_Check.exe we need below details. These details should be there inside Customer_Platform_Health_Check_Settings.json file.


Example JSON Structure

```json
{
  "css": {
    "database": "css_database",
    "user": "css_user",
    "password": "css_password",
    "host": "css_host",
    "port": 2284
  },
  "console": {
    "restURL": "http://console.rest.url/",
    "standalone_version": { "user": "console_username", "password": "console_password" },
    "enterprise_version": {
      "api_key": "console_api_key"
    }
  },
  "dashboard_url": "HDED Dashboard URL",
  "warnDays": 15,
  "html_file_path": "HTML FILE PATH"
}
```
Update the Customer_Platform_Health_Check_Settings.json file with the appropriate database, console, and user configurations.

### How It Works
The Customer_Platform_Health_Check.exe follows these steps to perform its operations:


**1. Initialization:**
The Customer_Platform_Health_Check.exe locates the Customer_Platform_Health_Check_Settings.json file in the current working directory:

This file contains critical configuration values, including:

- Warn Days
- CSS Database Name, Username, Password, Host, and Port
- AIP Console URL and Credentials
- HDED Dashborad URL
- HTML FILE PATH

Additionally, the EXE version (Version-1.0.0.4) is hardcoded.

**2. Log File Creation:**
The script creates a log file named Customer_Platform_Health_Check.log in the same directory to record all actions and errors.

**3. CSS Configuration Update:**
Fetches the CSS port number and hostname from the AIP Console.
Updates the CSS Port and CSS Hostname in the JSON configuration file.

**4. Fetching Data from AIP Console:**
Retrieves the License Key from the console.
Fetches the list of applications along with their details from the console.

**5. Updating License Keys:**
Updates the License Key for each application in the CSS database table (sys_licenses).

**6. Health Checks:**
Performs various health checks, including:

- **CSS Status:** Validates database connectivity.
- **License Key Status:** Verifies license key validity in CSS and Console.
- **Disk Space:** Checks if sufficient disk space is available on all the attached drives.
- **HDED Service Status:** Ensures the HDED service is running and its URL is functional.
- **Imaging Status:** Confirms whether Imaging viewer settings are set (URL & API key) in Imaging Console.

**7. Generating an HTML Report:**
- Collects data such as:
	1. 	Current Date and Time
	2. 	Host Name
	3. 	Application Details
- Creates an HTML file summarizing the results in a table format.
- Saves the file in the configured directory. 


### Main Functionalities(Methods):

- **update_css_details(json_file, host_name)**:- Updates CSS database configuration in the JSON file with the latest port and host details.

- **get_applications_from_console()**:- Fetches application details from the console.

- **get_the_license_from_the_console()**:- Retrieves the license key details from the console.

- **update_application_license_key(app_local_schema, console_license_key)**:- Updates the application license key in the CSS database.

- **check_postgres_status()**:- Verifies the status of the PostgreSQL database.

- **check_diskspace()**:- Checks the available disk space on the system.

- **is_aip_console_version_2x()**:- Checks if the AIP Console version is 2.x.

- **check_HDED()**:- Validates the status of the HDED service and its associated URL.

- **check_imaging_loaded()**:- Confirms whether imaging is loaded.

- **create_html_table(data, host_name, current_date_time, exe_version)**:- Generates an HTML table for the health check results.

### Logs
The script logs details of its execution inside Customer_Platform_Health_Check.log file.

### Error Handling
- Errors during execution are logged for debugging purposes.
- The script provides meaningful messages for configuration or runtime issues.

## Build the executable 
How to build Customer_Platform_Health_Check.exe ? 

### Deployment
Deploy Customer_Platform_Health_Check.exe inside Windows Task Scheduler using Customer_Platform_Health_Check.xml file.
How to fill Customer_Platform_Health_Check.xml file ? 

### Example HTML file.
![image](https://github.com/user-attachments/assets/5832d0c5-5871-4105-a566-0d0a557650d4)

### All possible return code from Customer_Platform_Health_Check 
![image](https://github.com/user-attachments/assets/eb4b2891-a835-49f2-bb17-e822a3ec7dad)

### Contributing

Contributions are welcome! Please open an issue or submit a pull request with your changes.



### Support

If you encounter any issues or have questions, please contact s.p@castsoftware.com

