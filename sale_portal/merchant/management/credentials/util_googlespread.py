from __future__ import print_function

import json

import httplib2
import os
import logging

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from oauth2client.service_account import ServiceAccountCredentials

_logger = logging.getLogger(__name__)


class GoogleSheetWithVerifyCode(object):
    CLIENT_SECRET_FILENAME = 'vnpay_google_spreadsheet_client_secret.json'
    CLIENT_SECRET_PATH = 'vnpay_google_spreadsheet_client_secret.json'

    def get_google_sheet_service_object(self):
        """Shows basic usage of the Sheets API.

        Creates a Sheets API service object and prints the names and majors of
        students in a sample spreadsheet:
        https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
        """

        # init here
        addon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        credential_dir = os.path.join(addon_path, 'credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        self.CLIENT_SECRET_PATH = os.path.join(credential_dir, self.CLIENT_SECRET_FILENAME)

        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.CLIENT_SECRET_PATH, scope)
        except Exception as e:
            _logger.info("ServiceAccountCredentials load client secrect file failed: %s" % str(e))
            return

        try:
            http = creds.authorize(httplib2.Http())
        except Exception as e:
            _logger.info("google script authorize failed: %s" % str(e))
            return

        try:
            discovery_url = ('https://sheets.googleapis.com/$discovery/rest?'
                             'version=v4')
            service = discovery.build('sheets', 'v4', http=http,
                                      discoveryServiceUrl=discovery_url, cache_discovery=False)
            return service
        except Exception as e:
            _logger.info("google script build discovery failed: %s" % str(e))
            return None

    def put_to_google_sheet(self, spread_id, range_name, range_values, cleared_range=None):

        service = self.get_google_sheet_service_object()

        if service:
            body = {
                'values': range_values
            }

            try:
                if cleared_range:
                    # clear here
                    service.spreadsheets().values().clear(
                        spreadsheetId=spread_id, range=cleared_range, body={}).execute()

                # update here
                service.spreadsheets().values().update(
                    spreadsheetId=spread_id, range=range_name,
                    valueInputOption="RAW", body=body).execute()
            except Exception as e:
                _logger.info("google script update data failed, spread_id: %s, error: %s" % (spread_id, e))

            _logger.info("google script update data successfully, spread_id: %s" % spread_id)

    def send(self, spread_id, sheet_name='', body_content=[], start_column='A', end_column='Z', start_row=1):
        if not spread_id or spread_id == '':
            _logger.info("Not found spread_id")
            return False

        cleared_range = sheet_name + '!' + str(start_column) + str(start_row) + ':' + str(end_column) + '1000000'

        total_rows = len(body_content) + start_row
        range_name = sheet_name + '!' + str(start_column) + str(start_row) + ':' + str(end_column) + str(total_rows)

        self.put_to_google_sheet(spread_id, range_name, body_content, cleared_range)

    def read(self, spreadsheet_id, range):
        try:
            service = self.get_google_sheet_service_object()

            if service:
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id, range=range
                ).execute()

                return result['values'] if 'values' in result else []
        except Exception as e:
            _logger.info("Google sheet read data failed, spread_id: %s, error: %s" % (spreadsheet_id, e))
            return None

    def create_new_sheet(self, spreadsheet_id, sheet_name):
        try:
            service = self.get_google_sheet_service_object()

            if service:
                request_body = {
                    'requests': [
                        {
                            'addSheet': {
                                'properties': {
                                    'title': sheet_name
                                }
                            }
                        }
                    ]
                }

                request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
                response = request.execute()

                if 'error' in response:
                    _logger.info("Google spreadsheet create new sheet failed, spread_id: %s, error: %s" % (
                        spreadsheet_id, json.dumps(response['error'])))
                    return None
                else:
                    try:
                        return response['replies']['addSheet']['properties']['title']
                    except Exception as e:
                        _logger.info("Google spreadsheet create new sheet failed, spread_id: %s, error: %s" % (
                        spreadsheet_id, e))
                        return None
        except Exception as e:
            _logger.info("Google sheet create new sheet failed, spread_id: %s, error: %s" % (spreadsheet_id, e))
            return None

    def get_sheet_info(self, spreadsheet_id):
        try:
            service = self.get_google_sheet_service_object()
            request = service.spreadsheets().get(spreadsheetId=spreadsheet_id)
            response = request.execute()

            if 'spreadsheetId' in response:
                _logger.info("Google sheet get sheet info, spread_id: %s, info: %s" % (spreadsheet_id, response))
                return response
            else:
                _logger.info("Google sheet get sheet info failed, spread_id: %s, error: %s" % (spreadsheet_id, response))
                return None
        except Exception as e:
            print("Google sheet get sheet info failed, spread_id: %s, error: %s" % (spreadsheet_id, e))
            _logger.info("Google sheet get sheet info failed, spread_id: %s, error: %s" % (spreadsheet_id, e))
            return None
