import requests


SEARCH_RESPONSES = {
    "yes": "The domain is available.",
    "no": "The domain is not available.",
    "offline": "The central registry for this domain is currently offline.",
    "system_busy": "All connections are busy.",
    "over_quota": "Over quota.",
    "error": "There was a syntax or registry error processing this domain."
}

REGISTER_RESPONSES = {
    "success": "The domain was successfully registered",
    "not_available": "The domain is not available",
    "insufficient_funds": "Not enough account balance to process this "
        "registration",
    "offline": "The central registry for this domain is currently offline",
    "system_busy": "All connections are busy",
    "over_quota": "See quota details below",
    "error": "There was a syntax or registry error processing this request"
}

DELETE_RESPONSES = {
    "success": "The domain was successfully deleted",
    "grace_expired": "The grace period has already expired",
    "too_soon": "Cannot delete a domain the first hour after registration",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}

RENEW_RESPONSES = {
    "success": "The domain was successfully renewed",
    "insufficient_funds": "Not enough account balance to process this renewal",
    "offline": "The central registry for this domain is currently offline",
    "error": "There was a syntax or registry error processing this request"
}


class Dynadot(object):
    API_URL = "https://api.dynadot.com/api2.html"
    API_KEY = None

    def __init__(self, api_key, *args, **kwargs):
        self.API_KEY = api_key
        self.payload = {"key": self.API_KEY}

    def delete(self, domain):
        """
        Delete a domain.
        """
        payload = self.payload.copy()
        payload.update({
            "command": "delete",
            "domain": domain
        })

        req = requests.get(self.API_URL, params=payload)
        response = self._check_response_status(req.text)

        if "error" in response:
            return self._error_response(response)

        return self._parse_delete_results(response[0].split(","))

    def search(self, domains):
        """
        Search for available domains.
        """
        payload = self.payload.copy()
        payload.update({"command": "search"})

        if domains:
            for index, domain in enumerate(domains):
                payload.update({"domain%d" % index: domain})

        req = requests.get(self.API_URL, params=payload)
        response = self._check_response_status(req.text)

        if "error" in response:
            return self._error_response(response)

        return self._parse_search_results(results=response)

    def register(self, domain, duration):
        """
        Register a domain.
        """
        payload = self.payload.copy()
        payload.update({
            "command": "register",
            "domain": domain,
            "duration": duration
        })

        req = requests.get(self.API_URL, params=payload)
        response = self._check_response_status(req.text)

        if "error" in response:
            return self._error_response(response)

        return self._parse_register_renew_results(response[0].split(","))

    def renew(self, domain, duration):
        """
        Renew a domain.
        """
        payload = self.payload.copy()
        payload.update({
            "command": "renew",
            "domain": domain,
            "duration": duration
        })

        req = requests.get(self.API_URL, params=payload)
        response = self._check_response_status(req.text)

        if "error" in response:
            return self._error_response(response)

        return self._parse_register_renew_results(response[0].split(","))

    def _parse_delete_results(self, result):
        """
        Parse delete result.
        """
        return {
            "result": result[0],
            "more_info": result[1]
        }

    def _parse_register_renew_results(self, result):
        """
        Parse registration result.
        """
        return {
            "result": result[0],
            "more_info": result[1],
            "expiration_date": result[2]
        }

    def _parse_search_results(self, results):
        """
        Parse search results.
        """
        loggins = []

        for result in results:
            result = result.split(",")
            if result:
                loggins.append({
                    "domain_param": result[0],
                    "domain": result[1],
                    "language": result[2],
                    "result": result[3],
                    "info": result[4]
                })
        return loggins

    def _check_response_status(self, response):
        """
        Check response for errors.
        """
        response_list = response.split("\n")
        status = response_list[0].split(",")

        if "error" in status:
            return status

        return response_list[2:-1]

    def _error_response(self, response):
        """
        Return error responses.
        """
        return {response[0]: response[1]}
