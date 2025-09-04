import logging
from requests.auth import HTTPBasicAuth
import requests
import json
import io

# Set up logging for the integration
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('IntegrationFunctions')

class BasicIntegration:
    def __init__(self, urlOneVizion="", loginOneVizion="", passOneVizion=""):
        """Initialize with proper logging"""
        logger.info("Initializing BasicIntegration")
        self.url_onevizion = urlOneVizion
        self.login_onevizion = loginOneVizion
        self.pass_onevizion = passOneVizion
        self.auth_onevizion = HTTPBasicAuth(self.login_onevizion, self.pass_onevizion)
        self.headers = {'Content-type': 'application/json', 'Content-Encoding': 'utf-8'}
        logger.info("Integration initialized successfully")


    def update_trackor(self, child_trackor_id, child_dict : dict):
        """Update a single trackor using OneVizion API"""
        url = 'https://{url_onevizion}/api/v3/trackors/{child_trackor_id}'.format(url_onevizion=self.url_onevizion,
                                                                                  child_trackor_id=child_trackor_id)
        answer = requests.put(url, data=json.dumps(child_dict), headers=self.headers, auth=self.auth_onevizion)
        if answer.ok:
            return answer.json()
        else:
            raise Exception(answer.text)

    def search_trackors(self, trackor_type: str, fields: list, filter: str):
        """Search for trackors through a filter using OneVizion API.

        Parameters
        ----------
        trackor_type : str
            Trackor Type of the Trackor for which data should be retrieved (e.g., BILL_OF_MATERIALS).
            Use the Trackor Type name, not the Trackor Type label.

        fields: list
            Comma separated list of Field names to return in response.
            Note: If Field doesn't exists HTTP 404 (Not found) will be returned

        filter: str
            Supported filter operators:
            equal(cf_name, value) or =(cf_name, value)
            greater(cf_name, value) or >(cf_name, value)
            less(cf_name, value) or <(cf_name, value)
            gt_today(cf_name, value = +0) or >=Today(cf_name, value = +0) [use + or - in front of value without spaces, if not specified +0 will be used]
            lt_today(cf_name, value = +0) or <=Today(cf_name, value = +0) [use + or - in front of value without spaces, if not specified +0 will be used]
            within(cf_name, value1, value2)
            not_equal(cf_name, value) or <>(cf_name, value)
            null(cf_name) or is_null(cf_name)
            is_not_null(cf_name)
            outer_equal(cf_name, value)
            outer_not_equal(cf_name, value)
            less_or_equal(cf_name, value) or <=(cf_name, value)
            greater_or_equal(cf_name, value) or >=(cf_name, value)
            this_week(cf_name, value = +0) [use + or - in front of value without spaces, if not specified +0 will be used]
            this_month(cf_name, value = +0) [use + or - in front of value without spaces, if not specified +0 will be used]
            this_quarter(cf_name, value = +0) [use + or - in front of value without spaces, if not specified +0 will be used] (equal to This FQ)
            this_year(cf_name, value = +0) [use + or - in front of value without spaces, if not specified +0 will be used] (equal to This FY)
            this_week_to_date(cf_name)
            this_month_to_date(cf_name)
            this_quarter_to_date(cf_name) (equal to This FQ to Dt)
            this_year_to_date(cf_name) (equal to This FY to Dt)
            field_equal(cf1_name, cf2_name) or =F(cf1_name, cf2_name)
            field_not_equal(cf1_name, cf2_name) or <>F(cf1_name, cf2_name)
            field_less(cf1_name, cf2_name) or <F(cf1_name, cf2_name)
            field_greater(cf1_name, cf2_name) or >F(cf1_name, cf2_name)
            field_less_or_equal(cf1_name, cf2_name) or <=F(cf1_name, cf2_name)
            field_greater_or_equal(cf1_name, cf2_name) or >=F(cf1_name, cf2_name)
            new(cf_name) or is_new(cf_name)
            not_new(cf_name) or is_not_new(cf_name)
            equal_myself(cf_name) or =Myself(cf_name)
            not_equal_myself(cf_name) or <>Myself(cf_name)

        Raises
        ------
        Exception
            If the response from onevizion is not ok
        """

        url = 'https://{url_onevizion}/api/v3/trackor_types/{trackor_type}/trackors/search?fields={fields}'.format(
            url_onevizion=self.url_onevizion,
            trackor_type=trackor_type, fields=",".join(fields))
        answer = requests.post(url, data=filter, headers=self.headers, auth=self.auth_onevizion)
        if answer.ok:
            return answer.json()
        else:
            raise Exception(answer.text)

    def create_trackor(self, child, child_field: dict, parent, parent_field: dict):
            """Create a trackor using OneVizion API"""
            url = 'https://{url_onevizion}/api/v3/trackor_types/{child_trackor_id}/trackors'.format(url_onevizion=self.url_onevizion,
                                                                                      child_trackor_id=child)
            data = {'fields': child_field, 'parents': [{'trackor_type': parent, 'filter': parent_field}]}

            logging.info(f"Creating trackor with data: {data}")

            answer = requests.post(url, data=json.dumps(data), headers=self.headers, auth=self.auth_onevizion)
            if answer.ok:
                return answer.json()
            else:
                logging.error(f"Error creating trackor: {answer.text}")
                raise Exception(answer.text)

    def create_trackor_noparent(self, child, child_field : dict,):
        """Create a trackor using OneVizion API"""
        url = 'https://{url_onevizion}/api/v3/trackor_types/{child_trackor_id}/trackors'.format(url_onevizion=self.url_onevizion,
                                                                                  child_trackor_id=child)
        data = {'fields': child_field}
        answer = requests.post(url, data=json.dumps(data), headers=self.headers, auth=self.auth_onevizion)
        if answer.ok:
            return answer.json()
        else:
            raise Exception(answer.text)

    def delete_trackor(self, trackor, track_id,):
        """Delete a trackor using OneVizion API"""
        url = 'https://{url_onevizion}/api/v3/trackor_types/{trackor_type}/trackors?trackor_id={trackor_ID}'.format(url_onevizion=self.url_onevizion,
                                                                                 trackor_type=trackor, trackor_ID=track_id)
        answer = requests.delete(url, data=json.dumps(trackor), headers=self.headers, auth=self.auth_onevizion)
        if answer.ok:
            return ("Trackor Deleted")
        else:
            raise Exception(answer.text)

    def get_file(self, trackor_id, field_name):
        """Retrieve file directly with enhanced error handling"""
        try:
            logger.info(f"Attempting to retrieve file from trackor {trackor_id}, field {field_name}")

            url = f'https://{self.url_onevizion}/api/v3/trackor/{trackor_id}/file/{field_name}'
            logger.debug(f"File URL: {url}")

            response = requests.get(
                url,
                headers=self.headers,
                auth=self.auth_onevizion,
                stream=True,
                timeout=30
            )

            logger.debug(f"Response status: {response.status_code}")

            if response.status_code == 404:
                logger.error(f"File not found (404) at {url}")
                return None, None
            elif not response.ok:
                logger.error(f"File retrieval failed: {response.status_code} - {response.text}")
                return None, None

            logger.info(f"Successfully retrieved file (size: {len(response.content)} bytes)")
            return response.headers, io.BytesIO(response.content)

        except Exception as e:
            logger.error(f"Error in get_file: {str(e)}", exc_info=True)
            return None, None

    def post_file(self, trackor_id: int, field_name: str, file_bytes: bytes, file_name: str,
                  mime_type: str = "application/pdf"):
        """Upload to EFile / Multiple EFiles via multipart/form-data. Returns (headers, json_or_text) on 200, else (None, None)."""
        import io
        import requests
        logger.info(f"Uploading file to trackor {trackor_id}, field {field_name}, name {file_name}")

        url = f"https://{self.url_onevizion}/api/v3/trackor/{trackor_id}/file/{field_name}"

        # Remove any Content-Type so requests can set proper multipart boundary
        headers = {k: v for k, v in (self.headers or {}).items() if k.lower() != "content-type"}

        # Ensure we have a file-like object
        fp = io.BytesIO(file_bytes) if isinstance(file_bytes, (bytes, bytearray)) else file_bytes

        try:
            resp = requests.post(
                url,
                params={"file_name": file_name},
                files={"file": (file_name, fp, mime_type)},
                headers=headers,
                auth=self.auth_onevizion,
                timeout=60,
                allow_redirects=True,
            )

            logger.debug(f"Upload response {resp.status_code}: {resp.text[:500] if resp.text else ''}")

            if resp.status_code == 200:
                # API says it returns blob_data_id; try JSON first
                try:
                    return resp.headers, resp.json()
                except ValueError:
                    return resp.headers, resp.text
            elif resp.status_code == 404:
                logger.error(f"Upload 404: check trackor_id/field_name {trackor_id}/{field_name}")
            else:
                logger.error(f"File upload failed {resp.status_code}: {resp.text}")
            return None, None
        except Exception as e:
            logger.error(f"Error in post_file: {e}", exc_info=True)
            return None, None


