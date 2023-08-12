# Generic imports
import json
import logging
import requests
import urllib.parse

class IndiWebManagerDummy:
    def __init__(self, config=None):
        pass
    def reset_server(self):
        pass
    def start_server(self):
        pass
    def stop_server(self):
        pass
    def probe_device_driver_connection(self, driver_name, device_name):
        pass
    def is_driver_started(self, driver_name):
        pass
    def get_running_driver_list(self):
        pass
    def get_running_driver(self):
        pass
    def restart_driver(self, driver_name):
        pass
    def start_driver(self, driver_name, check_started=True):
        pass
    def stop_driver(self, driver_name):
        pass

class IndiWebManagerClient:

    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        if config is None:
            config = dict(
                module="IndiWebManagedClient",
                host="localhost",
                port="8624",
                profile_name=""
            )
        self.host = config["host"]
        self.port = config["port"]
        self.profile_name = config["profile_name"]

    def reset_server(self):
        status, profile = self._get_server_status()
        if status:
            self.stop_server()
        self.start_server()

    def _get_server_status(self):
        """
        Reply: [{"status": "False"}, {"active_profile": ""}]
        :return: 
        """
        try:
            base_url = f"http://{self.host}:{self.port}"
            req = f"{base_url}/api/server/status"
            response = requests.get(req)
            self.logger.debug(f"_get_server_status - url {req} - code {response.status_code} - response:{response.text}")
            assert response.status_code == 200
            server_status = json.loads(response.text)
        except json.JSONDecodeError as e:
            msg = f"Cannot properly parse server status from {response.text} : {e}"
            self.logger.error(msg)
            raise RuntimeError(msg)
        except Exception as e:
            msg = f"Cannot get server status: {e}"
            self.logger.error(msg)
            raise RuntimeError(msg)
        else:
            status = [stat["status"] for stat in server_status][0] == "True"
            profile = [stat["active_profile"] for stat in server_status][0]
            return status, profile

    def start_server(self):
        try:
            base_url = f"http://{self.host}:{self.port}"
            req = f"{base_url}/api/server/start/{self.profile_name}"
            response = requests.post(req)
            self.logger.debug(f"start_server - url {req} - code {response.status_code} - response:{response.text}")
            assert response.status_code == 200
        except Exception as e:
            msg = f"Cannot start server: {e}"
            self.logger.error(msg)
            raise RuntimeError(msg)

    def stop_server(self):
        try:
            base_url = f"http://{self.host}:{self.port}"
            req = f"{base_url}/api/server/stop"
            response = requests.post(req)
            self.logger.debug(f"stop_server - url {req} - code {response.status_code} - response:{response.text}")
            assert response.status_code == 200
        except Exception as e:
            msg = f"Cannot start server: {e}"
            self.logger.error(msg)
            raise RuntimeError(msg)

    def is_driver_started(self, driver_name):
        return driver_name in self.get_running_driver_list()

    def get_running_driver_list(self):
        running_driver_list = self.get_running_driver()
        return [driver["name"] for driver in running_driver_list]

    def get_running_driver(self):
        """
            See documentation for the API here: https://github.com/knro/indiwebmanager
        :param driver_name:
        :return:
        """
        try:
            base_url = f"http://{self._indi_webserver_host}:" \
                       f"{self._indi_webserver_port}"
            req = f"{base_url}/api/server/drivers"
            response = requests.get(req)
            # self.logger.debug(f"get_running_driver - url {req} - code {response.status_code} - response :{response.text}")
            assert response.status_code == 200
            running_driver_list = json.loads(response.text)
        except json.JSONDecodeError as e:
            msg = f"Cannot properly parse list of running indi driver from {response.text} : {e}"
            self.logger.error(msg)
            raise RuntimeError(msg)
        except Exception as e:
            msg = f"Cannot get list of running indi driver : {e}"
            self.logger.error(msg)
            raise RuntimeError(msg)
        else:
            return running_driver_list

    def restart_driver(self, driver_name):
        """
            See documentation for the API here: https://github.com/knro/indiwebmanager
        :param driver_name:
        :return:
        """
        if self.is_driver_started(driver_name):
            try:
                base_url = f"http://{self._indi_webserver_host}:" \
                           f"{self._indi_webserver_port}"
                req = f"{base_url}/api/drivers/restart/" \
                      f"{urllib.parse.quote(driver_name)}"
                response = requests.post(req)
                self.logger.debug(
                    f"restart_driver {driver_name} - url {req} - code {response.status_code} - response:{response.text}")
                assert response.status_code == 200
            except Exception as e:
                msg = f"Cannot restart indi driver : {e}"
                self.logger.error(msg)
                raise RuntimeError(msg)
        else:
            self.start_driver(driver_name, check_started=False)

    def start_driver(self, driver_name, check_started=True):
        """
            See documentation for the API here: https://github.com/knro/indiwebmanager
        :param driver_name:
        :return:
        """
        if driver_name is None:
            self.logger.debug(f"In start_driver, no driver name provided, assuming webmanager has auto-start enabled")
            return
        if check_started and self.is_driver_started(driver_name):
            return
        try:
            base_url = f"http://{self._indi_webserver_host}:" \
                       f"{self._indi_webserver_port}"
            req = f"{base_url}/api/drivers/start/" \
                  f"{urllib.parse.quote(driver_name)}"
            response = requests.post(req)
            self.logger.debug(
                f"start_driver {driver_name} - url {req} - code {response.status_code} - response:{response.text}")
            assert response.status_code == 200
        except Exception as e:
            msg = f"Cannot start indi driver : {e}"
            self.logger.error(msg)
            raise RuntimeError(msg)

    def stop_driver(self, driver_name):
        """
            See documentation for the API here: https://github.com/knro/indiwebmanager
        :param driver_name:
        :return:
        """
        # No need to stop a driver that is not started
        if not self.is_driver_started(driver_name):
            self.logger.debug(f"No need to stop driver {driver_name} because it doesn't seems to be started")
            return
        try:
            # if driver_name not in ["ZWO CCD"]: #"Shelyak SPOX", "Arduino telescope controller", "ASI EAF", "Altair", "ZWO CCD"
            #    return
            base_url = f"http://{self._indi_webserver_host}:" \
                       f"{self._indi_webserver_port}"
            req = f"{base_url}/api/drivers/stop/" \
                  f"{urllib.parse.quote(driver_name)}"
            # self.logger.setLevel("DEBUG")
            # self.logger.warning(f"stop_driver {driver_name} DISABLED for now as it was randomly breaking indiserver")
            response = requests.post(req)
            self.logger.debug(
                f"stop_driver {driver_name} - url {req} - code {response.status_code} - response: {response.text}")
            assert response.status_code == 200
        except Exception as e:
            msg = f"Cannot stop indi driver : {e}"
            self.logger.error(msg)
            raise RuntimeError(msg)
