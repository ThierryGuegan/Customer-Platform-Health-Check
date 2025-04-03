import os
import psutil
import psycopg2
import requests
import json
import re
import logging
import subprocess

from datetime import datetime
from requests.auth import HTTPBasicAuth



class Platform():

    def __init__(self, css_database, css_user, css_password, css_host, css_port, console_restURL, console_user, console_password, console_api_key, warnDays, dashboard_url):
        self.css_database = css_database
        self.css_user = css_user
        self.css_password = css_password
        self.css_host = css_host
        self.css_port = int(css_port)

        self.console_restURL = console_restURL
        self.console_user = console_user
        self.console_password = console_password
        self.console_api_key = console_api_key
        self.warnDays = int(warnDays)
        self.dashboard_url = dashboard_url

    #this function updates the CSS port number inside Customer_Platform_Health_Check_Settings.json file.
    def update_css_details(self, json_file, host_name):

        try:
            method = "get"
            url=f"{self.console_restURL}api/settings/measurement-settings"
            auth = HTTPBasicAuth(f'{self.console_user}', f'{self.console_password}')
            headers = {"X-API-KEY": self.console_api_key}

            rsp = requests.request(method, url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                data = json.loads(rsp.text) 
                port_no = data["database"]["port"]
                host_name = data["database"]["host"]
                # print(port_no)

                with open(json_file, "r") as a_file:
                    json_object = json.load(a_file)
                json_object["css"]["port"] = port_no
                json_object["css"]["host"] = host_name
                self.css_host = host_name
                self.css_port = port_no

                with open(json_file, "w") as a_file:
                    json.dump(json_object, a_file)

                    print(f"updated the CSS port number as {port_no} and hostname as {host_name} inside Customer_Platform_Health_Check_Settings.json file.")
                    logging.info(f"updated the CSS port number as {port_no} and hostname as {host_name} inside Customer_Platform_Health_Check_Settings.json file.")

            else:
                port_no = 2282

                with open(json_file, "r") as a_file:
                    json_object = json.load(a_file)
                json_object["css"]["port"] = port_no
                json_object["css"]["host"] = host_name
                self.css_host = host_name
                self.css_port = port_no

                with open(json_file, "w") as a_file:
                    json.dump(json_object, a_file)

                    print(f"updated the CSS port number as {port_no} and hostname as {host_name} inside Customer_Platform_Health_Check_Settings.json file.")
                    logging.info(f"updated the CSS port number as {port_no} and hostname as {host_name} inside Customer_Platform_Health_Check_Settings.json file.")


        except Exception as e:
            print('some exception has occured! while executing update_css_details() function.\n Please resolve them or contact developers.')
            logging.error('some exception has occured! while executing update_css_details() function.\n Please resolve them or contact developers.')
            print(e)
            logging.error(e)
   
    def get_applications_from_console(self):
        method = "get"
        url=f"{self.console_restURL}api/applications"
        auth = HTTPBasicAuth(f'{self.console_user}', f'{self.console_password}')
        headers = {"X-API-KEY": self.console_api_key}

        try:
            #fetching the Application list and details.
            rsp = requests.request(method, url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                apps = json.loads(rsp.text) 
                apps_dict = {}
                for app in apps['applications']:
                    app_name = app["name"]
                    app_guid = app["guid"]
                    apps_dict[app_name] = app_guid
                return apps_dict
        except Exception as e:
            logging.error("get_applications_from_console() :- some exception has occured while getting applications from console! \n Please resolve them or contact developers")
            print('get_applications_from_console() :- some exception has occured while getting applications from console! \n Please resolve them or contact developers')
            logging.error(e)
            print(e)

    def get_the_license_from_the_console(self):
        method = "get"
        url=f"{self.console_restURL}api/settings/license"
        auth = HTTPBasicAuth(f'{self.console_user}', f'{self.console_password}')
        headers = {"X-API-KEY": self.console_api_key}

        try:
            #fetching the Application list and details.
            rsp = requests.request(method, url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                data = json.loads(rsp.text) 
                if data["license"]:
                    return data["license"]
                else:
                    return 0
        except Exception as e:
            logging.error("get_the_license_from_the_console() :- some exception has occured while getting application license from the console! \n Please resolve them or contact developers")
            print('get_the_license_from_the_console() :- some exception has occured while getting application license from the console! \n Please resolve them or contact developers')
            logging.error(e)
            print(e)

    def get_local_schema(self, guid):
        url=f"{self.console_restURL}api/aic/applications/{guid}"
        auth = HTTPBasicAuth(f'{self.console_user}', f'{self.console_password}')
        headers = {"X-API-KEY": self.console_api_key}

        try:
            #fetching the app schemas.
            rsp = requests.get(url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                data = json.loads(rsp.text) 

                for i in range(len(data["schemas"])):
                    if data["schemas"][i]["type"] == 'local':
                        return data["schemas"][i]["name"]

            else:
                print("Some error has occured! While fetching local schema.")
                print(rsp.text)

        except Exception as e:
            print('some exception has occured! While fetching local schema.\n Please resolve them or contact developers')
            print(e)

    def update_application_license_key(self, app_local_schema, console_license_key):

        try:
            # Establish a connection to the PostgreSQL server
            connection = psycopg2.connect(
                host=self.css_host,
                port=self.css_port,
                dbname=self.css_database,
                user=self.css_user,
                password=self.css_password
            )
            connection.autocommit = True 
            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()
            # if '.' in application_name:
            #     application_name = application_name.replace('.','_')
            # if '-' in application_name:
            #     application_name = application_name.replace('-','_')
            # Execute a simple query to fetch the license key from css
            cursor.execute(f"select * from {app_local_schema}.sys_licenses")
            # Fetch the result
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f"INSERT INTO {app_local_schema}.sys_licenses (license_code, license_id) VALUES ('{console_license_key}', 0)")
            else:    
                cursor.execute(f"UPDATE {app_local_schema}.sys_licenses SET license_code='{console_license_key}'")

            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            logging.error("update_application_license_key() :- some exception has occured while updating application license in the CSS! \n Please resolve them or contact developers")
            print('update_application_license_key() :- some exception has occured while updating application license in the CSS! \n Please resolve them or contact developers')
            logging.error(e)
            print(e)

    def check_postgres_status(self):
        try:
            # Establish a connection to the PostgreSQL server
            connection = psycopg2.connect(
                host=self.css_host,
                port=self.css_port,
                dbname=self.css_database,
                user=self.css_user,
                password=self.css_password
            )
            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()
            # Execute a simple query to fetch the current PostgreSQL version
            cursor.execute("SELECT version();")
            # Fetch the result
            result = cursor.fetchone()
            logging.info("check_postgres_status() :- OK - the database is up and accept connection.")
            # print("OK the database is up and accept connection.")
            # Close the cursor and connection
            cursor.close()
            connection.close()

            return "OK"
        except Exception as e:
            logging.info("check_postgres_status() :- KO - the database is not accepting connection).")
            logging.error("check_postgres_status() :- PostgreSQL connection failed:", e)
            # print("KO the database is not accepting connection.")
            # print("PostgreSQL connection failed:", e)
            return "KO - the database is not accepting connection"

    def calculate_remaining_days(self, date_string):
        # Get the current date
        current_date = datetime.now().date()

        # Parse the given date string
        given_date = datetime.strptime(date_string, "%Y-%m-%d").date()

        # Calculate the difference between the given date and the current date
        remaining_days = (given_date - current_date).days

        return remaining_days

    def check_the_licence_key_in_css(self, app_local_schema):
        try:
            # Establish a connection to the PostgreSQL server
            connection = psycopg2.connect(
                host=self.css_host,
                port=self.css_port,
                dbname=self.css_database,
                user=self.css_user,
                password=self.css_password
            )
            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()
            # if '.' in application_name:
            #     application_name = application_name.replace('.','_')
            # if '-' in application_name:
            #     application_name = application_name.replace('-','_')
            # Execute a simple query to fetch the license key from css
            cursor.execute(f"select * from {app_local_schema}.sys_licenses")
            # Fetch the result
            result = cursor.fetchone()
            if result is None:
                logging.info("check_the_licence_key_in_css() :- KO - at the date of the check the license key is not set.")
                # print('KO at the date of the check the license key has expired or is not set.')
                return 'KO - License key is not set'
            elif len(result[1]) > 0:
                # logging.info("Licence Key:"+ str(result[1]))
                # print("Licence Key:", result[1])

                expiry_date_pattern = '(\\d{8})'
                expiry_date = re.findall(expiry_date_pattern, result[1])
                if len(expiry_date) > 0: 
                    date_string = expiry_date[0][:4]+'-'+expiry_date[0][4:6]+'-'+expiry_date[0][6:]
                    remaining_days = self.calculate_remaining_days(date_string)
                    if remaining_days <= 0:
                        logging.info("check_the_licence_key_in_css() :- KO - at the date of the check the license key has expired.")
                        return 'KO - License key has expired'
                    elif remaining_days < self.warnDays:
                        logging.info(f'check_the_licence_key_in_css() :- WARN - the license key is about to expire in less than {remaining_days} calendar days.')
                        # print('OK the license is valid at the date of the check.') 
                        # print(f'WARN the license key is about to expire in less than {remaining_days} calendar days.')
                        return f'WARN (expires in less than {remaining_days} days.)'
                    else:
                        logging.info("check_the_licence_key_in_css() :- OK - the license is valid at the date of the check.")
                        # print('OK the license is valid at the date of the check.')
                        return 'OK'

            # Close the cursor and connection
            cursor.close()
            connection.close()
        except Exception as e:
            logging.error("check_the_licence_key_in_css() :- ERR - some error occurred that prevented to get the status -> "+str(e))
            if app_local_schema is None:
                return 'KO - Application declared but no analysis run'
            # print("ERR some error occurred that prevented to get the status -> ",e)
            # print("PostgreSQL connection failed:", e)
            return 'ERR'

    def check_the_licence_key_in_console(self):

        method = "get"
        url=f"{self.console_restURL}api/settings/license"
        auth = HTTPBasicAuth(self.console_user, self.console_password)
        headers = {"X-API-KEY": self.console_api_key}

        try:
            rsp = requests.request(method, url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                licence_key_details = json.loads(rsp.text) 

            if licence_key_details["license"] is None:
                logging.info('check_the_licence_key_in_console() :- KO - at the date of the check the license key is not set.')
                # print('KO at the date of the check the license key has expired or is not set.')
                return 'KO - License key is not set'
            elif len(licence_key_details["license"]) > 0:
                # logging.info("check_the_licence_key_in_console() :- Licence Key:" + str(licence_key_details["license"]))
                # print("Licence Key:", licence_key_details["license"])
                # logging.info("check_the_licence_key_in_console() :- Expiry Date:" + str(licence_key_details["expirationDate"]))
                # print("Expiry Date:", licence_key_details["expirationDate"])

                remaining_days = self.calculate_remaining_days(licence_key_details["expirationDate"])
                if remaining_days <= 0:
                    logging.info("check_the_licence_key_in_console() :- KO - at the date of the check the license key has expired.")
                    return 'KO - License key has expired'
                elif remaining_days < self.warnDays:
                    logging.info('check_the_licence_key_in_console() :- OK - the license is valid at the date of the check.')
                    # print('OK the license is valid at the date of the check.')
                    logging.info(f'check_the_licence_key_in_console() :- WARN - the license key is about to expire in less than {remaining_days} calendar days.') 
                    # print(f'WARN the license key is about to expire in less than {remaining_days} calendar days.')
                    return f'WARN - (expires in less than {remaining_days} days.)'
                else:
                    logging.info("check_the_licence_key_in_console() :- OK - the license is valid at the date of the check.")
                    # print('OK the license is valid at the date of the check.')
                    return 'OK'
        except Exception as e:
            logging.error("check_the_licence_key_in_console() :- ERR - some error occurred that prevented to get the status -> "+str(e))
            if str(e) == "cannot access local variable 'licence_key_details' where it is not associated with a value":
                return "KO - Imaging Console’s Initial configuration is not done"
            # print("PostgreSQL connection failed:", e)
            return 'ERR'

    def check_diskspace(self):
        try:
            drive = 'C:\\'
            usage = psutil.disk_usage(drive)
            percent_free = 100 - usage.percent

            if percent_free < 5:
                DiskSpace_status = ("KO - (Less than {:.0f}% free space remaining on {} drive)".format(5, drive))
                logging.info("KO - (Less than {:.0f}% free space remaining on {} drive)".format(5, drive))
            elif percent_free < 10:
                DiskSpace_status = ("WARN - (Less than {:.0f}% free space remaining on {} drive)".format(10, drive))
                logging.info("WARN - (Less than {:.0f}% free space remaining on {} drive)".format(10, drive))
            else:
                DiskSpace_status = "OK"
                logging.info("check_diskspace() :- OK - Have enough diskspace on C-Drive.")
            return DiskSpace_status
        except Exception as e:
            logging.error("check_diskspace() :- ERR - some exception has occured while executing this function: ", e)
            return "ERR"

    def is_aip_console_version_2x(self):

        method = "get"
        url=f"{self.console_restURL}api/"
        auth = HTTPBasicAuth(self.console_user, self.console_password)
        headers = {"X-API-KEY": self.console_api_key}

        try:
            rsp = requests.request(method, url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                res = json.loads(rsp.text) 
                aip_console_version = res["apiVersion"]

                # Extract the major version using a regular expression
                match = re.match(r'^(\d+)\.\d+\.\d+', aip_console_version)
                
                if match:
                    major_version = int(match.group(1))
                    return major_version == 2
                return False

        except Exception as e:
            logging.error("check_aip_console_version() :- ERR - some error occurred while checking aip console version -> "+str(e))
            return False

    def check_HDED(self):
        try:
            def check_HDED_status(service_name):
                for service in psutil.win_service_iter():
                    service_name = service.name()
                    if service_name_substring.lower() in service_name.lower():
                        try:
                            status = psutil.win_service_get(service_name).status()
                            if status == 'running':
                                logging.info(f"check_HDED() :- OK - '{service_name}' service is running.")
                                return 'OK', service_name
                            else:
                                logging.error(f"check_HDED() :- KO - '{service_name}' service is not running.")
                                return 'KO', service_name
                        except Exception as e:
                            logging.error(f"check_HDED() :- ERR - 'hded' service was not found.")
                            return 'ERR', 'hded'

            def check_REST_Client_status(url):
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        logging.info(f"check_REST_Client_status() :- OK - status code is '{response.status_code}' and '{url}' is working.")
                        return 'OK'
                    else:
                        logging.error(f"check_REST_Client_status() :- KO - status code is '{response.status_code}' and '{url}' is not working.")
                        return 'KO'
                except Exception as e:
                    logging.error(f"check_REST_Client_status() :- ERR - some exception has occured while executing this function: "+ str(e))
                    return 'ERR'
                
            if self.is_aip_console_version_2x():

                service_name_substring = "hded"
                HDED_service_status, service_name = check_HDED_status(service_name_substring)

                url = f"{self.dashboard_url}static/default.html"
                HDED_url_status = check_REST_Client_status(url)

                if HDED_service_status == 'OK' and HDED_url_status == 'OK':
                    return 'OK'
                elif HDED_service_status == 'KO':
                    return f"KO - '{service_name}' service is not running."
                elif HDED_service_status == 'ERR':
                    return f"ERR - '{service_name}' service was not found."
                elif HDED_url_status == 'KO':
                    return f"KO - '{url}' is not working."
                elif HDED_url_status == 'ERR':
                    return f"ERR - while accessing the url - '{url}'." 
                
            else:
                return "N/A for AIP Console Version-1.X"

        except Exception as e:
            logging.error("check_HDED() :- some exception has occured while executing this function:"+ str(e))
            return f"ERR - 'hded' service was not found.\n{e}"        

    def check_imaging_loaded(self):

        if self.is_aip_console_version_2x():

            method = "get"
            url=f"{self.console_restURL}api/settings/imaging-settings"
            auth = HTTPBasicAuth(self.console_user, self.console_password)
            headers = {"X-API-KEY": self.console_api_key}

            try:
                rsp = requests.request(method, url, auth=auth, headers=headers)
                # print(rsp.status_code)
                if rsp.status_code == 200:
                    imaging_details = json.loads(rsp.text) 
                    rsp_2 = requests.request('PUT', url, auth=auth, json=imaging_details, headers=headers)
                    if rsp_2.status_code == 202:
                        logging.info("check_imaging_loaded() :- OK - imaging is loaded.")
                        return 'OK'
                    else:
                        logging.info(f"check_imaging_loaded() :- KO - status code {rsp_2.status_code} {rsp_2.reason} - imaging is not loaded.")
                        return f'KO - status code {rsp_2.status_code} {rsp_2.reason}'
                else:
                    logging.error(f"check_imaging_loaded() :- KO - status code {rsp.status_code} {rsp.reason} - imaging is not loaded.")
                    return f'KO - status code {rsp.status_code} {rsp.reason}'

            except Exception as e:
                logging.error("check_imaging_loaded() :- ERR - some error occurred that prevented to get the status -> "+str(e))
                return f'ERR - {e}'
            
        else:
            return "N/A for AIP Console Version-1.X"
        
    def create_html_table(self, data, host_name, current_date_time, exe_version):
        
        table_html = f"<p> <b>Hostname:</b> {host_name} </p>  <p> <b>Generated on:</b> {current_date_time} </p> <p> <b>Customer_Platform_Health_Check.exe: </b> {exe_version} </p> <br/> <table style='border:1px solid black; border-collapse: collapse;'>\n"  # Adding 'border' attribute to add borders
        
        # Create table header
        header_row = data[0]
        table_html += "  <tr>\n"
        for header in header_row:
            table_html += f"    <th style='border:1px solid black; border-collapse: collapse;'>&nbsp&nbsp{header}&nbsp&nbsp</th>\n"
        table_html += "  </tr>\n"
        
        # Create table rows
        for row in data[1:]:
            table_html += "  <tr>\n"
            for i in range(len(row)):
                if i == 0:
                    table_html += f"<td style='border:1px solid black; border-collapse: collapse;'> {row[i]}</td>\n"
                elif row[i].startswith("WARN"):
                    table_html += f"<td style='border:1px solid black; border-collapse: collapse; text-align: center;'> <span style='color:#FCD12A;'>{row[i][:4]} </span><span style='color:black;'>{row[i][4:]}</span>\n  </td>"
                elif row[i].startswith("KO") or row[i].startswith("ERR"):
                    table_html += f"<td style='border:1px solid black; border-collapse: collapse; color:red; text-align: center;'> {row[i]} </td>\n"
                else:
                    table_html += f"<td style='border:1px solid black; border-collapse: collapse; text-align: center;'>{row[i]}</td>\n"

            table_html += "  </tr>\n"
        
        table_html += "</table>"
        return table_html


if __name__ == "__main__":

    try:
        current_directory = os.getcwd()

        with open(current_directory + '\\Customer_Platform_Health_Check_Settings.json') as f:
            # returns JSON object as a dictionary
            data = json.load(f)

        css_database = data['css']['database']
        css_user = data['css']['user']
        css_password = data['css']['password']
        css_host = data['css']['host']
        css_port = data['css']['port']
        console_restURL = data['console']['restURL']
        console_user = data['console']['standalone_version']['user']
        console_password = data['console']['standalone_version']['password']
        console_api_key = data['console']['enterprise_version']['api_key']
        warnDays = data['warnDays']
        dashboard_url = data['dashboard_url']
        html_file_path = data['html_file_path']
        exe_version = 'Version-1.0.0.2'

        isExist = os.path.exists(current_directory)

        logging.basicConfig(filename= current_directory + "\\Customer_Platform_Health_Check_Logs.txt", level=logging.INFO, format="%(asctime)s %(message)s", filemode='w')

        # logging.info('-----------------------------------------------------------------------------------------------------------------------------------------------')

        platform_obj = Platform(css_database, css_user, css_password, css_host, css_port, console_restURL, console_user, console_password, console_api_key, warnDays, dashboard_url)

        current_date_time = datetime.now()

        cmd = "hostname"
        returned_value = subprocess.check_output(cmd, shell=True)  # returns the exit code in unix
        host_name = returned_value.decode("utf-8").strip().lower()

        platform_obj.update_css_details(current_directory + '\\Customer_Platform_Health_Check_Settings.json', host_name)

        table_data = [["Application Name", "CSS Status", "License Key in CSS", "License Key in Console", "DiskSpace in C-Drive", "Engineering/Health Dashboard", "Imaging is loaded"]]

        applications = platform_obj.get_applications_from_console()

        console_license_key = platform_obj.get_the_license_from_the_console()

        if applications:
            for application, app_guid in applications.items():

                app_local_schema = platform_obj.get_local_schema(app_guid)

                if console_license_key != 0:
                    platform_obj.update_application_license_key(app_local_schema, console_license_key)

                logging.info('-----------------------------------------------------------------------------------------')

                logging.info(f'checking platform health for {application}.....')
                # Call the function to check the CSS status
                CSS_Status = platform_obj.check_postgres_status()

                CSS_LK_status = platform_obj.check_the_licence_key_in_css(app_local_schema)

                Console_LK_status = platform_obj.check_the_licence_key_in_console()

                DiskSpace_status = platform_obj.check_diskspace()

                HDED_status = platform_obj.check_HDED()

                Imaging_is_loaded = platform_obj.check_imaging_loaded()

                table_data.append([application, CSS_Status, CSS_LK_status, Console_LK_status, DiskSpace_status, HDED_status, Imaging_is_loaded])

        else:
            logging.info(f'checking platform health.....')
            # Call the function to check the CSS status
            CSS_Status = platform_obj.check_postgres_status()

            Console_LK_status = platform_obj.check_the_licence_key_in_console()

            DiskSpace_status = platform_obj.check_diskspace()

            HDED_status = platform_obj.check_HDED()

            Imaging_is_loaded = platform_obj.check_imaging_loaded()

            table_data.append([ 'N/A', CSS_Status, 'N/A', Console_LK_status, DiskSpace_status, HDED_status, Imaging_is_loaded])

        logging.info('-----------------------------------------------------------------------------------------')

        # Generate HTML table
        html_table = platform_obj.create_html_table(table_data, host_name, current_date_time, exe_version)

        # Write HTML to a file
        local_html_path = html_file_path + f'\\{host_name}.html' 
        with open( local_html_path, "w") as file:
            file.write(html_table)

        print(f"{host_name}.html is created and saved at location -> {local_html_path}")
        logging.info(f"{host_name}.html is created and saved at location -> {local_html_path}")

    except Exception as e:
        print('some exception has occured! while executing __main__ function.\n Please resolve them or contact developers.')
        logging.error('some exception has occured! while executing __main__ function.\n Please resolve them or contact developers.')
        print(e)
        logging.error(e)